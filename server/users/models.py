from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extra info for each user.
    One-to-one with Django's built-in auth.User.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Basic profile info
    ROLE_SUPER_ADMIN = "super_admin"
    ROLE_ADMIN = "admin"
    ROLE_RECRUITER = "recruiter"
    ROLE_EMPLOYEE = "employee"
    ROLE_CHOICES = [
        (ROLE_SUPER_ADMIN, "Super Admin"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_RECRUITER, "Recruiter"),
        (ROLE_EMPLOYEE, "Employee"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_EMPLOYEE,
        help_text="RBAC role for application access",
    )
    telephone = models.CharField(max_length=20, blank=True)
    avatar = models.FileField(
        upload_to="avatars/",
        null=True,
        blank=True,
        help_text="Profile picture or avatar",
    )
    department = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)

    # Preferences
    language = models.CharField(
        max_length=20,
        blank=True,
        default="en",
        help_text="Preferred language code, e.g. en, fr, de",
    )
    timezone = models.CharField(
        max_length=64,
        blank=True,
        default="UTC",
        help_text="IANA timezone name, e.g. Europe/Berlin, Asia/Karachi",
    )

    # Password metadata (actual password is stored hashed in auth.User.password)
    password_last_changed = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the password was last changed",
    )

    def __str__(self):
        return f"Profile for {self.user.username}"


class LoginHistory(models.Model):
    """
    Tracks login / logout events for a user.
    """

    LOGIN = "login"
    LOGOUT = "logout"

    EVENT_TYPE_CHOICES = [
        (LOGIN, "Login"),
        (LOGOUT, "Logout"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_history",
    )
    # login / logout
    type = models.CharField(
        max_length=10,
        choices=EVENT_TYPE_CHOICES,
    )

    # Device & context
    device = models.CharField(
        max_length=255,
        blank=True,
        help_text="Browser / device info",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="City / country / IP-based location",
    )

    # Timestamps
    time = models.DateTimeField(
        auto_now_add=True,
        help_text="Time of login/logout event",
    )
    logout_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="If this row represents a logout or session end",
    )

    def __str__(self):
        return f"{self.user.username} - {self.type} at {self.time}"
