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
    
    # Social Links
    github_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="GitHub profile URL"
    )
    linkedin_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="LinkedIn profile URL"
    )

    linkedin_scrape_status = models.CharField(
        max_length=20,
        default='idle',
        choices=[
            ('idle', 'Idle'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        help_text="Current status of the LinkedIn background scrape"
    )

    social_insights = models.JSONField(
        default=dict,
        blank=True,
        help_text="Scraped data from social profiles (e.g. LinkedIn)"
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


class LinkedInScrapingActivity(models.Model):
    """
    Tracks LinkedIn scraping activity to enforce daily limits.
    Helps prevent account flags by staying under LinkedIn's radar.
    """
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    profile_url = models.URLField()
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'linkedin_scraping_activity'
        ordering = ['-timestamp']
    
    @classmethod
    def get_today_count(cls):
        """Get number of successful scrapes today."""
        from django.utils import timezone
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return cls.objects.filter(
            timestamp__gte=today_start,
            success=True
        ).count()
    
    @classmethod
    def can_scrape_today(cls, daily_limit=50):
        """Check if we're under daily limit."""
        return cls.get_today_count() < daily_limit
    
    @classmethod
    def log_scrape(cls, profile_url, success=True, error=None):
        """Log a scraping attempt."""
        return cls.objects.create(
            profile_url=profile_url,
            success=success,
            error_message=error
        )
