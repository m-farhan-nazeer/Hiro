"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.decorators.csrf import csrf_exempt

from django.contrib import admin

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

from applicants.views import ApplicantViewSet, applicant_resume
from users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    ChangePasswordView,
    LoginHistoryView,
)

router = DefaultRouter()
router.register(r"applicants", ApplicantViewSet, basename="applicant")

urlpatterns = [
    path("", include(router.urls)),  
    path("admin/", admin.site.urls),

    # Users
    path("users/register/", RegisterView.as_view(), name="user-register"),
    path("users/login/", LoginView.as_view(), name="user-login"),
    path("users/logout/", LogoutView.as_view(), name="user-logout"),
    path("users/me/", MeView.as_view(), name="user-me"),
    path("users/change-password/", ChangePasswordView.as_view(), name="user-change-password"),
    path("users/login-history/", LoginHistoryView.as_view(), name="user-login-history"),

    # Applicants
    path("applicants/<int:pk>/resume/", applicant_resume, name="applicant-resume"),
    path("", include(router.urls)),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
