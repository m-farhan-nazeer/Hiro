from django.contrib import admin
from .models import Applicant, ApplicantProfile


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'telephone', 'source']
    search_fields = ['name', 'email']
    list_filter = ['source']


@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'extracted_at', 'total_experience_years', 'extraction_source']
    search_fields = ['applicant__name', 'applicant__email']
    readonly_fields = ['extracted_at', 'raw_extraction']
    list_filter = ['extracted_at']
