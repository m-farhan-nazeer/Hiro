from rest_framework import viewsets
from .models import Applicant
from .serializers import ApplicantSerializer


class ApplicantViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Applicant:
    - GET /applicants/          -> list
    - POST /applicants/         -> create
    - GET /applicants/<id>/     -> retrieve
    - PUT /applicants/<id>/     -> full update
    - PATCH /applicants/<id>/   -> partial update
    - DELETE /applicants/<id>/  -> delete
    """
    queryset = Applicant.objects.all().order_by("-applied_date")
    serializer_class = ApplicantSerializer
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework import viewsets
from .models import Applicant
from .serializers import ApplicantSerializer


class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all().order_by("-applied_date")
    serializer_class = ApplicantSerializer


def applicant_resume(request, pk):
    """
    Return the resume stored as BLOB for this applicant.
    URL: /applicants/<pk>/resume/
    """
    applicant = get_object_or_404(Applicant, pk=pk)

    if not applicant.resume:
        return HttpResponse(status=404)

    # Assuming resumes are PDFs – browser will try to display inline
    response = HttpResponse(
        applicant.resume,
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'inline; filename="resume_{pk}.pdf"'
    return response
