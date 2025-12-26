from rest_framework import serializers
from .models import Applicant, ApplicantProfile


class ApplicantProfileSerializer(serializers.ModelSerializer):
    """Serializer for ApplicantProfile - exposes structured resume insights"""
    
    applicant_name = serializers.CharField(source='applicant.name', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    
    class Meta:
        model = ApplicantProfile
        fields = [
            'id',
            'applicant',
            'applicant_name',
            'applicant_email',
            'extracted_at',
            'extraction_source',
            'skills',
            'experience',
            'education',
            'certifications',
            'summary',
            'total_experience_years',
            'github_url',
            'linkedin_url',
            'social_insights',
        ]
        read_only_fields = ['id', 'extracted_at', 'applicant_name', 'applicant_email']



class ApplicantSerializer(serializers.ModelSerializer):
    # Enriched fields from related applications (when filtering by job)
    status = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    jobAppliedFor = serializers.SerializerMethodField()
    appliedDate = serializers.SerializerMethodField()
    has_resume = serializers.SerializerMethodField()
    resume_url = serializers.SerializerMethodField()

    class Meta:
        model = Applicant
        fields = [
            "id",
            "name",
            "email",
            "telephone",
            "prior_experience",
            "source",
            "skill_set",
            "status",
            "score",
            "jobAppliedFor",
            "appliedDate",
            "has_resume",
            "resume_url",
        ]

    def get_status(self, obj):
        """Get status from the most recent application, or from job-filtered application if job_id is in query params"""
        request = self.context.get("request")
        if request:
            job_id = request.query_params.get('job', None)
            if job_id:
                # Get application for this specific job
                application = obj.applications.filter(job_id=job_id).first()
                if application:
                    return application.status
            else:
                # Get most recent application
                application = obj.applications.order_by('-date').first()
                if application:
                    return application.status
        return None

    def get_score(self, obj):
        """Get score from the most recent application, or from job-filtered application if job_id is in query params"""
        request = self.context.get("request")
        if request:
            job_id = request.query_params.get('job', None)
            if job_id:
                application = obj.applications.filter(job_id=job_id).first()
                if application:
                    return str(application.score) if application.score else None
            else:
                application = obj.applications.order_by('-date').first()
                if application:
                    return str(application.score) if application.score else None
        return None

    def get_jobAppliedFor(self, obj):
        """Get job title from the most recent application, or from job-filtered application if job_id is in query params"""
        request = self.context.get("request")
        if request:
            job_id = request.query_params.get('job', None)
            if job_id:
                application = obj.applications.filter(job_id=job_id).first()
                if application:
                    return application.job.title
            else:
                application = obj.applications.order_by('-date').first()
                if application:
                    return application.job.title
        return None

    def get_appliedDate(self, obj):
        """Get applied date from the most recent application, or from job-filtered application if job_id is in query params"""
        request = self.context.get("request")
        if request:
            job_id = request.query_params.get('job', None)
            if job_id:
                application = obj.applications.filter(job_id=job_id).first()
                if application:
                    return application.date.isoformat()
            else:
                application = obj.applications.order_by('-date').first()
                if application:
                    return application.date.isoformat()
        return None

    def get_has_resume(self, obj):
        """Check if applicant has a resume in any application"""
        request = self.context.get("request")
        if request:
            job_id = request.query_params.get('job', None)
            if job_id:
                application = obj.applications.filter(job_id=job_id).first()
                if application:
                    return bool(application.resume)
            else:
                application = obj.applications.order_by('-date').first()
                if application:
                    return bool(application.resume)
        return False

    def get_resume_url(self, obj):
        """Get resume URL from the most recent application, or from job-filtered application if job_id is in query params"""
        request = self.context.get("request")
        if request:
            job_id = request.query_params.get('job', None)
            if job_id:
                application = obj.applications.filter(job_id=job_id).first()
                if application and application.resume:
                    return request.build_absolute_uri(f"/api/applications/{application.pk}/resume/")
            else:
                application = obj.applications.order_by('-date').first()
                if application and application.resume:
                    return request.build_absolute_uri(f"/api/applications/{application.pk}/resume/")
        return None
