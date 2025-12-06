from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
import logging
import os
import tempfile

from .models import Application
from applicants.models import Applicant
from posts.models import Job

logger = logging.getLogger(__name__)


class ApplicationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating applications from frontend submission.
    Handles applicant creation/lookup and application creation.
    """
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    resume_file = serializers.FileField(required=True)
    job = serializers.IntegerField(required=True)  # job_id
    score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        default=0
    )
    status = serializers.ChoiceField(
        choices=Application.STATUS_CHOICES,
        required=False,
        default="pending"
    )

    def validate_job(self, value):
        """Validate that the job exists"""
        try:
            job = Job.objects.get(pk=value)
            return job
        except Job.DoesNotExist:
            raise ValidationError(f"Job with id {value} does not exist.")

    def validate_email(self, value):
        """Normalize email to lowercase"""
        return value.lower().strip()

    def create(self, validated_data):
        """
        Create or get applicant by email, then create application.
        Handles all the logic for applicant lookup/creation and application creation.
        """
        email = validated_data["email"]
        name = validated_data["name"]
        job = validated_data["job"]
        resume_file = validated_data["resume_file"]
        score = validated_data.get("score", 0)
        status = validated_data.get("status", "pending")

        try:
            # Get or create applicant by email
            applicant, created = Applicant.objects.get_or_create(
                email=email,
                defaults={"name": name},
            )
            
            logger.info(
                f"Applicant {'created' if created else 'found'}: {email} (ID: {applicant.id})"
            )
            
            # Update name if applicant already exists (in case name changed)
            if not created and applicant.name != name:
                applicant.name = name
                applicant.save()
                logger.info(f"Updated applicant name for {email}")

            # Check if application already exists (prevent duplicates)
            if Application.objects.filter(applicant=applicant, job=job).exists():
                logger.warning(
                    f"Duplicate application attempt: applicant {applicant.id} for job {job.id}"
                )
                raise ValidationError(
                    {
                        "error": "Application already exists",
                        "message": "You have already applied for this job position.",
                    }
                )

            # Read resume file content
            resume_bytes = resume_file.read()
            
            if not resume_bytes:
                raise ValidationError({"resume_file": "Resume file is empty"})

            # 1) Create application first so resume is stored in DB
            application = Application.objects.create(
                applicant=applicant,
                job=job,
                resume=resume_bytes,
                score=score,
                status=status,
            )

            logger.info(
                f"Application created: ID {application.id}, "
                f"Applicant: {applicant.email}, Job: {job.id}"
            )

            # 2) Run MLOps pipeline to compute score
            tmp_path = None
            try:
                # Import MLOps utils lazily so missing ML deps
                # won't break Django startup; failures are logged.
                try:
                    from rag.utils import (
                        store_job_description,
                        rank_resume_against_job,
                    )
                except ImportError as e:
                    logger.error(
                        "MLOps dependencies not available, skipping scoring for "
                        "application %s: %s",
                        application.id,
                        str(e),
                        exc_info=True,
                    )
                    return application

                # Build job description text for vector store
                job_text_parts = [
                    job.title or "",
                    job.description or "",
                    f"Status: {job.status}" if getattr(job, "status", None) else "",
                    f"Job type: {job.jobtype}" if getattr(job, "jobtype", None) else "",
                    f"Job time: {job.jobtime}" if getattr(job, "jobtime", None) else "",
                    f"Shift: {job.shift}" if getattr(job, "shift", None) else "",
                    f"Skills: {job.required_skills}" if getattr(job, "required_skills", None) else "",
                    f"Domain: {job.domain}" if getattr(job, "domain", None) else "",
                ]
                job_text = "\n\n".join([p for p in job_text_parts if p])

                if job_text:
                    try:
                        store_job_description(job_text)
                    except Exception as e:
                        logger.error(
                            "Failed to store job description in vector DB for application %s: %s",
                            application.id,
                            str(e),
                            exc_info=True,
                        )

                # Write resume bytes to a temporary file for ranking
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                    tmp_file.write(resume_bytes)
                    tmp_path = tmp_file.name

                try:
                    generated_score = rank_resume_against_job(tmp_path)
                except Exception as e:
                    logger.error(
                        "Failed to generate score for application %s: %s",
                        application.id,
                        str(e),
                        exc_info=True,
                    )
                else:
                    # Update application with generated score
                    application.score = generated_score
                    application.save(update_fields=["score"])
                    logger.info(
                        "Updated application %s with generated score: %s",
                        application.id,
                        generated_score,
                    )
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        logger.warning("Failed to remove temp resume file %s", tmp_path)

            return application

        except IntegrityError as e:
            logger.error(f"Integrity error creating application: {str(e)}")
            raise ValidationError(
                {"error": "Database integrity error", "message": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected error creating application: {str(e)}")
            raise ValidationError(
                {"error": "Failed to create application", "message": str(e)}
            )

    def to_representation(self, instance):
        """Return application data in standard format"""
        return ApplicationSerializer(instance, context=self.context).to_representation(instance)


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Standard serializer for Application model (used for GET, PUT, PATCH, DELETE)
    """
    applicant_name = serializers.CharField(source='applicant.name', read_only=True)
    applicant_email = serializers.EmailField(source='applicant.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    # Used for uploading the resume file (frontend / Postman)
    resume_file = serializers.FileField(
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Application
        fields = [
            'id',
            'applicant',
            'applicant_name',
            'applicant_email',
            'job',
            'job_title',
            'resume',
            'resume_file',
            'score',
            'status',
            'date',
        ]
        extra_kwargs = {
            # Don't allow client to send raw bytes directly
            "resume": {"read_only": True},
        }

    def create(self, validated_data):
        # Get uploaded file (if any)
        resume_file = validated_data.pop("resume_file", None)

        if resume_file:
            # Read file content as bytes and store in BinaryField
            validated_data["resume"] = resume_file.read()

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle resume file on update as well
        resume_file = validated_data.pop("resume_file", None)

        if resume_file:
            instance.resume = resume_file.read()

        # Let DRF handle other fields
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Control how resume appears in API output:
        - Do NOT return raw bytes
        - Expose has_resume + resume_url
        """
        data = super().to_representation(instance)

        # Remove raw bytes field from output if present
        data.pop("resume", None)

        has_resume = bool(instance.resume)
        data["has_resume"] = has_resume

        # Build URL for resume endpoint if resume exists
        if has_resume:
            request = self.context.get("request")
            if request is not None:
                # absolute URL
                data["resume_url"] = request.build_absolute_uri(
                    f"/api/applications/{instance.pk}/resume/"
                )
            else:
                # fallback relative URL
                data["resume_url"] = f"/api/applications/{instance.pk}/resume/"
        else:
            data["resume_url"] = None

        return data
