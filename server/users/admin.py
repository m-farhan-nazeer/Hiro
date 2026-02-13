from django.contrib import admin
from .models import UserProfile, LoginHistory


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "department", "position")
    list_filter = ("role", "department")
    search_fields = ("user__username", "user__email", "department", "position")


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "time", "logout_time")
    list_filter = ("type",)
    search_fields = ("user__username", "user__email")
