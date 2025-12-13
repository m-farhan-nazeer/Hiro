from django.db import models
from applicants.models import Applicant
from posts.models import Job


class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
    ]

    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    resume = models.BinaryField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = [['applicant', 'job']]  # Prevent duplicate applications

    def __str__(self):
        return f"{self.applicant.name} - {self.job.title}"
