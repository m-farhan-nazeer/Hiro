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
