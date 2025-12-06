from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import logging
from .models import Application
from .serializers import ApplicationSerializer, ApplicationCreateSerializer
from applicants.models import Applicant
from posts.models import Job

logger = logging.getLogger(__name__)


class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/applications/ -> List all applications
    GET /api/applications/?job=<job_id> -> List applications for a specific job
    POST /api/applications/ -> Create a new application
    
    For POST, accepts either:
    1. ApplicationCreateSerializer format (name, email, resume_file, job) - for frontend submissions
    2. ApplicationSerializer format (applicant, job, resume_file) - for direct API calls
    """
    queryset = Application.objects.all().order_by("-date")
    
    def get_queryset(self):
        """
        Optionally filter applications by job ID and/or status if provided in query parameters
        """
        queryset = super().get_queryset()
        job_id = self.request.query_params.get('job', None)
        status = self.request.query_params.get('status', None)
        
        if job_id is not None:
            try:
                job_id = int(job_id)
                queryset = queryset.filter(job_id=job_id)
            except (ValueError, TypeError):
                # If job_id is not a valid integer, return all applications
                pass
        
        if status is not None and status != '':
            # Convert capitalized status to lowercase for database lookup
            status_lower = status.lower()
            queryset = queryset.filter(status=status_lower)
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializer for POST vs GET"""
        if self.request.method == 'POST':
            # Check if request has 'name' and 'email' (new submission format)
            # or 'applicant' (direct API format)
            data = self.request.data
            if 'name' in data and 'email' in data:
                return ApplicationCreateSerializer
        return ApplicationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Handle application creation with proper error handling and logging
        """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={'request': request})
        
        try:
            logger.info(f"Creating application - Data: {request.data.keys()}")
            serializer.is_valid(raise_exception=True)
            application = serializer.save()
            
            # Return response using standard ApplicationSerializer format
            response_serializer = ApplicationSerializer(application, context={'request': request})
            logger.info(f"Application created successfully: ID {application.id}")
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            error_detail = e.detail
            if isinstance(error_detail, dict):
                error_message = error_detail
            elif isinstance(error_detail, list):
                error_message = {'error': error_detail[0] if error_detail else 'Validation error'}
            else:
                error_message = {'error': str(error_detail)}
            
            logger.warning(f"Validation error creating application: {error_message}")
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Unexpected error creating application: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to create application', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ApplicationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/applications/<pk>/ -> Retrieve a single application
    PUT /api/applications/<pk>/ -> Full update
    PATCH /api/applications/<pk>/ -> Partial update
    DELETE /api/applications/<pk>/ -> Delete
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    
    def update(self, request, *args, **kwargs):
        """Handle update with proper error handling"""
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            error_detail = e.detail
            if isinstance(error_detail, dict):
                error_message = error_detail
            elif isinstance(error_detail, list):
                error_message = {'error': error_detail[0] if error_detail else 'Validation error'}
            else:
                error_message = {'error': str(error_detail)}
            logger.warning(f"Validation error updating application: {error_message}")
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error updating application: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Failed to update application', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomerStatisticAPIView(APIView):
    """
    GET /api/crm/customers-statistic -> Get applicant statistics
    """
    def get(self, request):
        # Get total applicants count (unique applicants who have applications)
        total_applicants = Applicant.objects.filter(
            applications__isnull=False
        ).distinct().count()
        
        # Get shortlisted count (unique applicants with shortlisted applications)
        shortlisted_count = Applicant.objects.filter(
            applications__status='shortlisted'
        ).distinct().count()
        
        # Get hired count (unique applicants with hired applications)
        hired_count = Applicant.objects.filter(
            applications__status='hired'
        ).distinct().count()
        
        # Calculate growth (comparing last 3 months vs previous 3 months)
        three_months_ago = (timezone.now() - timedelta(days=90)).date()
        six_months_ago = (timezone.now() - timedelta(days=180)).date()
        
        # Total applicants in last 3 months
        recent_total = Applicant.objects.filter(
            applications__date__gte=three_months_ago
        ).distinct().count()
        
        # Total applicants in previous 3 months
        previous_total = Applicant.objects.filter(
            applications__date__gte=six_months_ago,
            applications__date__lt=three_months_ago
        ).distinct().count()
        
        total_growth = ((recent_total - previous_total) / previous_total * 100) if previous_total > 0 else 0
        
        # Shortlisted growth
        recent_shortlisted = Applicant.objects.filter(
            applications__status='shortlisted',
            applications__date__gte=three_months_ago
        ).distinct().count()
        
        previous_shortlisted = Applicant.objects.filter(
            applications__status='shortlisted',
            applications__date__gte=six_months_ago,
            applications__date__lt=three_months_ago
        ).distinct().count()
        
        shortlisted_growth = ((recent_shortlisted - previous_shortlisted) / previous_shortlisted * 100) if previous_shortlisted > 0 else 0
        
        # Hired growth
        recent_hired = Applicant.objects.filter(
            applications__status='hired',
            applications__date__gte=three_months_ago
        ).distinct().count()
        
        previous_hired = Applicant.objects.filter(
            applications__status='hired',
            applications__date__gte=six_months_ago,
            applications__date__lt=three_months_ago
        ).distinct().count()
        
        hired_growth = ((recent_hired - previous_hired) / previous_hired * 100) if previous_hired > 0 else 0
        
        return Response({
            'totalCustomers': {
                'value': total_applicants,
                'growShrink': round(total_growth, 2)
            },
            'activeCustomers': {
                'value': shortlisted_count,
                'growShrink': round(shortlisted_growth, 2)
            },
            'newCustomers': {
                'value': hired_count,
                'growShrink': round(hired_growth, 2)
            }
        })


class SalesDashboardAPIView(APIView):
    """
    POST /api/sales/dashboard -> Get dashboard data
    """
    def post(self, request):
        # Statistics
        total_applicants = Applicant.objects.filter(
            applications__isnull=False
        ).distinct().count()
        active_jobs = Job.objects.filter(status='active').count()
        hired_count = Application.objects.filter(status='hired').count()
        
        # Calculate growth (last 3 months vs previous 3 months)
        three_months_ago = (timezone.now() - timedelta(days=90)).date()
        six_months_ago = (timezone.now() - timedelta(days=180)).date()
        
        recent_applicants = Applicant.objects.filter(
            applications__date__gte=three_months_ago
        ).distinct().count()
        previous_applicants = Applicant.objects.filter(
            applications__date__gte=six_months_ago,
            applications__date__lt=three_months_ago
        ).distinct().count()
        applicants_growth = ((recent_applicants - previous_applicants) / previous_applicants * 100) if previous_applicants > 0 else 0
        
        recent_jobs = Job.objects.filter(date__gte=three_months_ago).count()
        previous_jobs = Job.objects.filter(
            date__gte=six_months_ago,
            date__lt=three_months_ago
        ).count()
        jobs_growth = ((recent_jobs - previous_jobs) / previous_jobs * 100) if previous_jobs > 0 else 0
        
        recent_hired = Application.objects.filter(status='hired', date__gte=three_months_ago).count()
        previous_hired = Application.objects.filter(
            status='hired',
            date__gte=six_months_ago,
            date__lt=three_months_ago
        ).count()
        hired_growth = ((recent_hired - previous_hired) / previous_hired * 100) if previous_hired > 0 else 0
        
        # Latest applicants (last 4 applications)
        latest_applications = Application.objects.select_related('applicant', 'job').order_by('-date')[:4]
        latest_applicant_data = [{
            'name': app.applicant.name,
            'email': app.applicant.email,
            'status': app.status,
            'telephone': app.applicant.telephone or '',
            'job': app.job.title,
            'score': float(app.score) if app.score else 0
        } for app in latest_applications]
        
        # Latest jobs (last 3 jobs with applicant count)
        latest_jobs = Job.objects.annotate(
            total_applicants=Count('applications')
        ).order_by('-date')[:3]
        job_data = [{
            'title': job.title,
            'pay': 0,  # Not in model, using placeholder
            'description': job.description,
            'status': job.status,
            'date': job.date.isoformat(),
            'jobtype': job.jobtype,
            'jobtime': job.jobtime,
            'shift': job.shift or '',
            'reqskills': job.required_skills.split(',') if job.required_skills else [],
            'domain': job.domain or '',
            'totalapplicants': job.total_applicants
        } for job in latest_jobs]
        
        # Sales report data (applications over last 6 months by month)
        months = []
        application_counts = []
        for i in range(6):
            month_start = (timezone.now() - timedelta(days=30 * (6 - i))).date()
            month_end = month_start + timedelta(days=30)
            month_name = month_start.strftime('%b')
            months.append(month_name)
            count = Application.objects.filter(date__gte=month_start, date__lt=month_end).count()
            application_counts.append(count)
        
        # Recruitment by categories (by application status: hired, shortlisted, pending, rejected)
        status_counts = Application.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Create a dictionary for easy lookup
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        # Order: hired, shortlisted, pending, rejected
        recruitment_by_categories = {
            'labels': ['Hired', 'Shortlisted', 'Pending', 'Rejected'],
            'data': [
                status_dict.get('hired', 0),
                status_dict.get('shortlisted', 0),
                status_dict.get('pending', 0),
                status_dict.get('rejected', 0)
            ]
        }
        
        return Response({
            'statisticData': {
                'revenue': {
                    'value': total_applicants,
                    'growShrink': round(applicants_growth, 2)
                },
                'orders': {
                    'value': active_jobs,
                    'growShrink': round(jobs_growth, 2)
                },
                'purchases': {
                    'value': hired_count,
                    'growShrink': round(hired_growth, 2)
                }
            },
            'latestApplicantData': latest_applicant_data,
            'jobData': job_data,
            'salesReportData': {
                'series': [{
                    'name': 'Applications',
                    'data': application_counts
                }],
                'categories': months
            },
            'recruitmentByCategoriesData': recruitment_by_categories
        })


def application_resume(request, pk):
    """
    Return the resume stored as BLOB for this application.
    URL: /api/applications/<pk>/resume/
    """
    application = get_object_or_404(Application, pk=pk)

    if not application.resume:
        return HttpResponse(status=404)

    # Assuming resumes are PDFs – browser will try to display inline
    response = HttpResponse(
        application.resume,
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'inline; filename="resume_{pk}.pdf"'
    return response
