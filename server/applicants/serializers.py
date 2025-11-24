from rest_framework import serializers
from .models import Applicant


class ApplicantSerializer(serializers.ModelSerializer):
    # Used for uploading the resume file (frontend / Postman)
    resume_file = serializers.FileField(
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Applicant
        fields = [
            "id",
            "name",
            "status",
            "email",
            "telephone",
            "job_applied_for",
            "applied_date",
            "score",
            "prior_experience",
            "source",
            "skill_set",
            "resume",       # stored as BLOB (bytea) in DB
            "resume_file",  # virtual field for uploads
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
                    f"/applicants/{instance.pk}/resume/"
                )
            else:
                # fallback relative URL
                data["resume_url"] = f"/applicants/{instance.pk}/resume/"
        else:
            data["resume_url"] = None

        return data
