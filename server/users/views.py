from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, permissions, authentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, LoginHistory
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    LoginHistorySerializer,
)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication that does NOT enforce CSRF.
    Only for API use (Postman / SPA). Don't use this blindly in prod.
    """
    def enforce_csrf(self, request):
        return  # skip CSRF check


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    """
    POST /users/register/
    Create a new user + profile.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # no auth, open endpoint

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # init password_last_changed
        profile = getattr(user, "profile", None)
        if profile:
            profile.password_last_changed = timezone.now()
            profile.save()

        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    """
    POST /users/login/
    Body: { "username": "...", "password": "..." }
    Creates a Django session (cookie).
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # CSRF-free

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # create session
        login(request, user)

        LoginHistory.objects.create(
            user=user,
            type=LoginHistory.LOGIN,
            device=request.META.get("HTTP_USER_AGENT", ""),
            location="",
        )

        return Response(
            UserSerializer(user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    """
    POST /users/logout/
    Clears session + logs logout.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request):
        user = request.user

        last_login = (
            LoginHistory.objects.filter(user=user, type=LoginHistory.LOGIN)
            .order_by("-time")
            .first()
        )
        if last_login and last_login.logout_time is None:
            last_login.logout_time = timezone.now()
            last_login.save()

        LoginHistory.objects.create(
            user=user,
            type=LoginHistory.LOGOUT,
            device=request.META.get("HTTP_USER_AGENT", ""),
            location="",
        )

        logout(request)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class MeView(APIView):
    """
    GET /users/me/
    Uses session cookie to get current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request):
        return Response(
            UserSerializer(request.user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ChangePasswordView(APIView):
    """
    POST /users/change-password/
    Body: { "old_password": "...", "new_password": "..." }
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        user: User = request.user

        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Old password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        profile = getattr(user, "profile", None)
        if profile:
            profile.password_last_changed = timezone.now()
            profile.save()

        # keep user logged in after password change
        login(request, user)

        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class LoginHistoryView(APIView):
    """
    GET /users/login-history/
    List recent login/logout events for current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self, request):
        qs = (
            LoginHistory.objects.filter(user=request.user)
            .order_by("-time")[:50]
        )
        serializer = LoginHistorySerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
