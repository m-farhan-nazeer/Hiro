from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import UserProfile, LoginHistory


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "role",
            "telephone",
            "avatar",
            "department",
            "position",
            "language",
            "timezone",
            "password_last_changed",
        ]
        read_only_fields = ["password_last_changed", "role"]


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user info + attached profile.
    Password is NOT exposed here.
    """
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    For user registration.
    Creates both User and UserProfile.
    """
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    telephone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    department = serializers.CharField(write_only=True, required=False, allow_blank=True)
    position = serializers.CharField(write_only=True, required=False, allow_blank=True)
    language = serializers.CharField(write_only=True, required=False, allow_blank=True)
    timezone = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
            "telephone",
            "department",
            "position",
            "language",
            "timezone",
        ]
        extra_kwargs = {
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        telephone = validated_data.pop("telephone", "")
        department = validated_data.pop("department", "")
        position = validated_data.pop("position", "")
        language = validated_data.pop("language", "en")
        timezone = validated_data.pop("timezone", "UTC")

        validated_data.pop("password_confirm", None)
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(
            user=user,
            telephone=telephone,
            department=department,
            position=position,
            language=language or "en",
            timezone=timezone or "UTC",
        )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = [
            "id",
            "type",
            "device",
            "location",
            "time",
            "logout_time",
        ]
