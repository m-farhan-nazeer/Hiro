from django.conf import settings
from django.db import models


class JobQuerySet(models.QuerySet):
    def visible_to(self, user):
        if not user or not getattr(user, "is_authenticated", False):
            return self.none()
        if getattr(user, "is_superuser", False):
            return self.all()

        profile = getattr(user, "profile", None)
        role = getattr(profile, "role", None)
        if role in {"admin", "super_admin"}:
            return self.all()

        if user.has_perm("posts.view_all_jobs"):
            return self.all()

        return self.filter(created_by=user)



# / → Job list

# /job/create/ → Add new

# /job/<id>/ → Detail

# /job/<id>/update/ → Edit

# /job/<id>/delete/ → Delete

class Job(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('paused', 'Paused'),
    ]
    JOB_TYPE_CHOICES = [
        ('onsite', 'Onsite'),
        ('remote', 'Remote'),
    ]
    JOB_TIME_CHOICES = [
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    date = models.DateField(auto_now_add=True)
    jobtype = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    jobtime = models.CharField(max_length=20, choices=JOB_TIME_CHOICES)
    shift = models.CharField(max_length=50, blank=True, null=True)
    required_skills = models.TextField()
    domain = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="jobs",
        null=True,
        blank=True,
        help_text="The user who posted this job",
    )

    # Scoring weights (sum must be 100)
    weight_experience = models.FloatField(default=5)
    weight_skills = models.FloatField(default=25)
    weight_projects = models.FloatField(default=50)
    weight_education = models.FloatField(default=10)
    weight_institute = models.FloatField(default=10)

    objects = JobQuerySet.as_manager()

    def total_applicants(self):
        return self.applicants.count()

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ("view_all_jobs", "Can view all jobs"),
            ("manage_all_jobs", "Can manage all jobs"),
        ]
