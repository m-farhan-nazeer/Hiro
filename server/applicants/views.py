from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Applicant
from .serializers import ApplicantSerializer
from applications.models import Application


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
    queryset = Applicant.objects.all().order_by("-id")
    serializer_class = ApplicantSerializer
    
    def get_queryset(self):
        """
        Optionally filter applicants by job ID if provided in query parameters.
        Returns applicants who have applications for the specified job.
        """
        queryset = super().get_queryset()
        job_id = self.request.query_params.get('job', None)
        
        # Prefetch related applications for better performance
        queryset = queryset.prefetch_related('applications__job')
        
        if job_id is not None:
            try:
                job_id = int(job_id)
                # Filter applicants who have applications for this job
                application_ids = Application.objects.filter(job_id=job_id).values_list('applicant_id', flat=True)
                queryset = queryset.filter(id__in=application_ids)
            except (ValueError, TypeError):
                # If job_id is not a valid integer, return all applicants
                pass
        
        return queryset


def applicant_resume(request, pk):
    """
    Return the resume stored as BLOB for this applicant.
    URL: /applicants/<pk>/resume/
    Note: Applicants don't have resumes directly - resumes are stored in Applications.
    """
    applicant = get_object_or_404(Applicant, pk=pk)
    
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
