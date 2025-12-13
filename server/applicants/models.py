from django.db import models


# applicants/models.py

class Applicant(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # Ensure email is unique
    telephone = models.CharField(max_length=20, blank=True)
    prior_experience = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    skill_set = models.TextField(blank=True, help_text="Comma-separated skills")

    class Meta:
        ordering = ['-id']  # Order by newest first

    def __str__(self):
        return self.name


class ApplicantProfile(models.Model):
    """
    Stores structured information extracted from applicant's resume.
    One-to-one relationship with Applicant.
    """
    applicant = models.OneToOneField(
        Applicant,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Extraction metadata
    extracted_at = models.DateTimeField(auto_now_add=True)
    extraction_source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Which resume/application was used for extraction"
    )
    
    # Structured data (JSON fields for flexibility)
    skills = models.JSONField(
        default=list,
        blank=True,
        help_text="List of skills: [{name, category, proficiency}]"
    )
    experience = models.JSONField(
        default=list,
        blank=True,
        help_text="Work experience: [{company, title, duration, description}]"
    )
    education = models.JSONField(
        default=list,
        blank=True,
        help_text="Education: [{institution, degree, field, year}]"
    )
    certifications = models.JSONField(
        default=list,
        blank=True,
        help_text="Certifications: [{name, issuer, year}]"
    )
    
    # Summary fields
    summary = models.TextField(
        blank=True,
        help_text="Professional summary/bio extracted from resume"
    )
    total_experience_years = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Total years of professional experience"
    )
    
    # Raw extraction for reference
    raw_extraction = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complete LLM response for debugging"
    )
    
    class Meta:
        ordering = ['-extracted_at']
        verbose_name = "Applicant Profile"
        verbose_name_plural = "Applicant Profiles"
    
    def __str__(self):
        return f"Profile: {self.applicant.name}"
