from rest_framework import viewsets, status as http_status, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Applicant, ApplicantProfile
from .serializers import ApplicantSerializer, ApplicantProfileSerializer
from applications.models import Application
from posts.models import Job
from users.authentication import CsrfExemptSessionAuthentication
import logging
import asyncio
from asgiref.sync import async_to_sync
from .scrapers import LinkedInScraper

logger = logging.getLogger(__name__)


class ApplicantViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Applicant:
    - GET /applicants/          -> list
    - GET /applicants/?job=<job_id> -> list applicants for a specific job
    - POST /applicants/         -> create
    - GET /applicants/<id>/     -> retrieve
    - PUT /applicants/<id>/     -> full update
    - PATCH /applicants/<id>/   -> partial update
    - DELETE /applicants/<id>/  -> delete
    """
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Applicant.objects.all().order_by("-id")
    serializer_class = ApplicantSerializer
    
    def get_queryset(self):
        """
        Optionally filter applicants by job ID if provided in query parameters.
        Returns applicants who have applications for the specified job.
        """
        queryset = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return Applicant.objects.none()

        visible_jobs = Job.objects.visible_to(user)
        queryset = queryset.filter(applications__job__in=visible_jobs).distinct()
        job_id = self.request.query_params.get('job', None)
        
        # Prefetch related applications for better performance
        queryset = queryset.prefetch_related('applications__job')
        
        if job_id is not None:
            try:
                job_id = int(job_id)
                if not visible_jobs.filter(id=job_id).exists():
                    return Applicant.objects.none()
                # Filter applicants who have applications for this job
                application_ids = Application.objects.filter(job_id=job_id).values_list('applicant_id', flat=True)
                queryset = queryset.filter(id__in=application_ids)
            except (ValueError, TypeError):
                # If job_id is not a valid integer, return all applicants
                pass
        
        return queryset


def _user_can_access_applicant(user, applicant: Applicant) -> bool:
    if not user or not user.is_authenticated:
        return False
    visible_jobs = Job.objects.visible_to(user)
    return Application.objects.filter(applicant=applicant, job__in=visible_jobs).exists()


def applicant_resume(request, pk):
    """
    Return the resume stored as BLOB for this applicant.
    URL: /applicants/<pk>/resume/
    Note: Applicants don't have resumes directly - resumes are stored in Applications.
    """
    applicant = get_object_or_404(Applicant, pk=pk)

    if not _user_can_access_applicant(request.user, applicant):
        return HttpResponse(status=404)
    
    # Get the most recent application's resume for this applicant
    application = Application.objects.filter(applicant=applicant).order_by('-date').first()
    
    if not application or not application.resume:
        return HttpResponse(status=404)

    # Assuming resumes are PDFs – browser will try to display inline
    response = HttpResponse(
        application.resume,
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'inline; filename="resume_{pk}.pdf"'
    return response


# ============================================
# APPLICANT PROFILE API ENDPOINTS
# ============================================

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_applicant_profile(request, applicant_id):
    """
    GET /api/applicants/<id>/profile/
    
    Returns structured resume insights for an applicant.
    If profile doesn't exist, triggers extraction from most recent resume.
    
    Response:
        200: Profile data (existing or newly created)
        404: Applicant not found or no resume available
        500: Extraction failed
    """
    try:
        applicant = Applicant.objects.get(pk=applicant_id)
    except Applicant.DoesNotExist:
        return Response(
            {'error': 'Applicant not found'},
            status=http_status.HTTP_404_NOT_FOUND
        )

    if not _user_can_access_applicant(request.user, applicant):
        return Response({'error': 'Applicant not found'}, status=http_status.HTTP_404_NOT_FOUND)
    
    # Check if profile exists
    try:
        profile = applicant.profile
        serializer = ApplicantProfileSerializer(profile)
        return Response(serializer.data)
    except ApplicantProfile.DoesNotExist:
        # Profile doesn't exist, trigger extraction
        logger.info(f"Profile not found for applicant {applicant_id}, triggering extraction")
        return trigger_profile_extraction(applicant)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def refresh_applicant_profile(request, applicant_id):
    """
    POST /api/applicants/<id>/profile/refresh/
    
    Force re-extraction of profile from latest resume.
    Deletes existing profile and creates a new one.
    
    Response:
        201: New profile created
        404: Applicant not found or no resume available
        500: Extraction failed
    """
    try:
        applicant = Applicant.objects.get(pk=applicant_id)
    except Applicant.DoesNotExist:
        return Response(
            {'error': 'Applicant not found'},
            status=http_status.HTTP_404_NOT_FOUND
        )

    if not _user_can_access_applicant(request.user, applicant):
        return Response({'error': 'Applicant not found'}, status=http_status.HTTP_404_NOT_FOUND)
    
    # Delete existing profile if exists
    ApplicantProfile.objects.filter(applicant=applicant).delete()
    logger.info(f"Deleted existing profile for applicant {applicant_id}, re-extracting")
    
    # Trigger new extraction
    return trigger_profile_extraction(applicant)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([permissions.IsAuthenticated])
def scrape_social_profile(request, applicant_id):
    """
    POST /api/applicants/<id>/social-scrape/
    
    Triggers LinkedIn scraping for the applicant.
    Uses the stored linkedin_url.
    """
    try:
        applicant = Applicant.objects.get(pk=applicant_id)
    except Applicant.DoesNotExist:
        return Response({'error': 'Applicant not found'}, status=404)

    if not _user_can_access_applicant(request.user, applicant):
        return Response({'error': 'Applicant not found'}, status=404)

    try:
        profile = applicant.profile
    except ApplicantProfile.DoesNotExist:
        return Response({'error': 'Applicant profile not found'}, status=404)

    if not profile.linkedin_url:
        return Response({'error': 'No LinkedIn URL found for this applicant'}, status=400)

    # Check rate limiting
    from .models import LinkedInScrapingActivity
    daily_limit = 50
    if not LinkedInScrapingActivity.can_scrape_today(daily_limit):
        count = LinkedInScrapingActivity.get_today_count()
        return Response({
            'error': f'Daily limit reached ({count}/{daily_limit}). Try again tomorrow.'
        }, status=429)

    logger.info(f"Triggering background LinkedIn scrape for applicant {applicant_id} at {profile.linkedin_url}")

    # Update status to processing
    profile.linkedin_scrape_status = 'processing'
    profile.save(update_fields=['linkedin_scrape_status'])

    try:
        from .tasks import BackgroundTask, scrape_linkedin_async
        BackgroundTask.run(
            scrape_linkedin_async,
            applicant_id=applicant.id,
            linkedin_url=profile.linkedin_url
        )
        
        return Response({
            'message': 'LinkedIn scraping started in background. Please wait a few moments for profiles to update.',
            'status': 'processing'
        }, status=http_status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Failed to trigger background scraping: {e}")
        return Response({'error': str(e)}, status=500)




def trigger_profile_extraction(applicant):
    """
    Helper function to extract profile from applicant's most recent resume.
    
    Args:
        applicant: Applicant instance
    
    Returns:
        Response with profile data or error
    """
    # Get most recent application with resume
    application = applicant.applications.filter(
        resume__isnull=False
    ).exclude(resume=b'').order_by('-date').first()
    
    if not application or not application.resume:
        logger.warning(f"No resume found for applicant {applicant.id}")
        return Response(
            {'error': 'No resume found for this applicant'},
            status=http_status.HTTP_404_NOT_FOUND
        )
    
    try:
        # Import extraction function
        from rag.resume_extractor import extract_resume_insights
        
        logger.info(f"Extracting insights for applicant {applicant.id} from application {application.id}")
        
        # Extract insights
        insights = extract_resume_insights(
            resume_bytes=application.resume,
            filename=f"resume_{applicant.id}.pdf"
        )
        
        # Create profile
        # Create or update profile (handle race conditions)
        profile, created = ApplicantProfile.objects.update_or_create(
            applicant=applicant,
            defaults={
                'extraction_source': f"Application #{application.id}",
                'skills': insights.get('skills', []),
                'experience': insights.get('experience', []),
                'education': insights.get('education', []),
                'certifications': insights.get('certifications', []),
                'summary': insights.get('summary', ''),
                'total_experience_years': insights.get('total_experience_years'),
                'github_url': insights.get('github_url'),
                'linkedin_url': insights.get('linkedin_url'),
                'raw_extraction': insights
            }
        )
        
        logger.info(f"Profile created successfully for applicant {applicant.id}")
        
        serializer = ApplicantProfileSerializer(profile)
        return Response(serializer.data, status=http_status.HTTP_201_CREATED)
        
    except ImportError as e:
        logger.error(f"MLOps dependencies not available for applicant {applicant.id}: {str(e)}")
        return Response(
            {'error': 'Resume extraction service unavailable', 'detail': str(e)},
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Failed to extract profile for applicant {applicant.id}: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to extract resume insights', 'detail': str(e)},
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
        )
