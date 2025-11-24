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
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    job_applied_for = models.CharField(max_length=255)
    applied_date = models.DateField(auto_now_add=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    # ⬇️ store resume as binary blob in Postgres (bytea)
    resume = models.BinaryField(null=True, blank=True)
    prior_experience = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    skill_set = models.TextField(blank=True, help_text="Comma-separated skills")

    def __str__(self):
        return f"{self.name} - {self.job_applied_for}"
