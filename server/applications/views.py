from rest_framework import generics, status, permissions
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
from django.db.models.functions import TruncMonth
from users.authentication import CsrfExemptSessionAuthentication

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
    authentication_classes = (CsrfExemptSessionAuthentication,)
    queryset = Application.objects.all().order_by("-date")
    
    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        Optionally filter applications by job ID and/or status if provided in query parameters
        """
        queryset = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return Application.objects.none()

        visible_jobs = Job.objects.visible_to(user)
        queryset = queryset.filter(job__in=visible_jobs)

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
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Application.objects.none()
        visible_jobs = Job.objects.visible_to(user)
        return super().get_queryset().filter(job__in=visible_jobs)
    
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
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        visible_jobs = Job.objects.visible_to(request.user)
        applicant_qs = Applicant.objects.filter(applications__job__in=visible_jobs).distinct()

        # Get total applicants count (unique applicants who have applications)
        total_applicants = applicant_qs.count()
        
        # Get shortlisted count (unique applicants with shortlisted applications)
        shortlisted_count = applicant_qs.filter(
            applications__status='shortlisted'
        ).distinct().count()
        
        # Get hired count (unique applicants with hired applications)
        hired_count = applicant_qs.filter(
            applications__status='hired'
        ).distinct().count()
        
        # Calculate growth (comparing last 3 months vs previous 3 months)
        three_months_ago = (timezone.now() - timedelta(days=90)).date()
        six_months_ago = (timezone.now() - timedelta(days=180)).date()
        
        # Total applicants in last 3 months
        recent_total = applicant_qs.filter(
            applications__date__gte=three_months_ago
        ).distinct().count()
        
        # Total applicants in previous 3 months
        previous_total = applicant_qs.filter(
            applications__date__gte=six_months_ago,
            applications__date__lt=three_months_ago
        ).distinct().count()
        
        total_growth = ((recent_total - previous_total) / previous_total * 100) if previous_total > 0 else 0
        
        # Shortlisted growth
        recent_shortlisted = applicant_qs.filter(
            applications__status='shortlisted',
            applications__date__gte=three_months_ago
        ).distinct().count()
        
        previous_shortlisted = applicant_qs.filter(
            applications__status='shortlisted',
            applications__date__gte=six_months_ago,
            applications__date__lt=three_months_ago
        ).distinct().count()
        
        shortlisted_growth = ((recent_shortlisted - previous_shortlisted) / previous_shortlisted * 100) if previous_shortlisted > 0 else 0
        
        # Hired growth
        recent_hired = applicant_qs.filter(
            applications__status='hired',
            applications__date__gte=three_months_ago
        ).distinct().count()
        
        previous_hired = applicant_qs.filter(
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
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        visible_jobs = Job.objects.visible_to(request.user)
        application_qs = Application.objects.filter(job__in=visible_jobs)
        applicant_qs = Applicant.objects.filter(applications__job__in=visible_jobs).distinct()

        # Statistics
        total_applicants = applicant_qs.count()
        active_jobs = visible_jobs.filter(status='active').count()
        hired_count = application_qs.filter(status='hired').count()
        
        # Calculate growth (last 3 months vs previous 3 months)
        three_months_ago = (timezone.now() - timedelta(days=90)).date()
        six_months_ago = (timezone.now() - timedelta(days=180)).date()
        
        recent_applicants = applicant_qs.filter(
            applications__date__gte=three_months_ago
        ).distinct().count()
        previous_applicants = applicant_qs.filter(
            applications__date__gte=six_months_ago,
            applications__date__lt=three_months_ago
        ).distinct().count()
        applicants_growth = ((recent_applicants - previous_applicants) / previous_applicants * 100) if previous_applicants > 0 else 0
        
        recent_jobs = visible_jobs.filter(date__gte=three_months_ago).count()
        previous_jobs = visible_jobs.filter(
            date__gte=six_months_ago,
            date__lt=three_months_ago
        ).count()
        jobs_growth = ((recent_jobs - previous_jobs) / previous_jobs * 100) if previous_jobs > 0 else 0
        
        recent_hired = application_qs.filter(status='hired', date__gte=three_months_ago).count()
        previous_hired = application_qs.filter(
            status='hired',
            date__gte=six_months_ago,
            date__lt=three_months_ago
        ).count()
        hired_growth = ((recent_hired - previous_hired) / previous_hired * 100) if previous_hired > 0 else 0
        
        # Latest applicants (last 4 applications)
        latest_applications = application_qs.select_related('applicant', 'job').order_by('-date')[:4]
        latest_applicant_data = [{
            'name': app.applicant.name,
            'email': app.applicant.email,
            'status': app.status,
            'telephone': app.applicant.telephone or '',
            'job': app.job.title,
            'score': float(app.score) if app.score else 0
        } for app in latest_applications]
        
        # Latest jobs (last 3 jobs with applicant count)
        latest_jobs = visible_jobs.annotate(
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
        
        # Recruitment report data (applications over last 6 months by calendar month)
        six_months_ago_date = (timezone.now() - timedelta(days=180)).replace(day=1).date()
        
        monthly_counts = (
            application_qs.filter(date__gte=six_months_ago_date)
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        
        # Convert QuerySet to a dict for easy lookup
        counts_dict = {item['month']: item['count'] for item in monthly_counts}
        
        # Ensure we have data for the last 6 months, even if missing in DB
        months = []
        application_counts = []
        
        # Start from 5 months ago to include current month (total 6)
        current_date = timezone.now().date().replace(day=1)
        for i in range(5, -1, -1):
            target_month = (current_date - timedelta(days=i*31)).replace(day=1) 
            # Note: timedelta(days=i*31) is a bit loose, 
            # better to use a loop or relativedelta if available, 
            # but Hiro seems to use standard datetime.
            
            # Refined month calculation without external dependencies
            year = current_date.year
            month = current_date.month - i
            while month <= 0:
                month += 12
                year -= 1
            
            month_date = timezone.datetime(year, month, 1).date()
            months.append(month_date.strftime('%b'))
            application_counts.append(counts_dict.get(month_date, 0))
        
        # Recruitment by categories (by application status: hired, shortlisted, pending, rejected)
        status_counts = application_qs.values('status').annotate(
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
    if not request.user or not request.user.is_authenticated:
        return HttpResponse(status=403)

    application = get_object_or_404(Application, pk=pk)
    if not Job.objects.visible_to(request.user).filter(id=application.job_id).exists():
        return HttpResponse(status=404)

    if not application.resume:
        return HttpResponse(status=404)

    # Assuming resumes are PDFs – browser will try to display inline
    response = HttpResponse(
        application.resume,
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'inline; filename="resume_{pk}.pdf"'
    return response
