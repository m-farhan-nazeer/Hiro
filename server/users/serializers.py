from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import UserProfile, LoginHistory


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "role",
            "name",
            "telephone",
            "avatar",
            "department",
            "position",
            "language",
            "timezone",
            "password_last_changed",
        ]
        read_only_fields = ["password_last_changed", "role"]

    def get_name(self, obj):
        user = obj.user
        return f"{user.first_name} {user.last_name}".strip() or user.username


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


class AccountSettingUpdateSerializer(serializers.Serializer):
    """
    Serializer to handle updates for both User and UserProfile.
    Matches the structure expected by the frontend.
    """
    # User fields
    name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    # Profile fields
    title = serializers.CharField(required=False, allow_blank=True)
    telephone = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)
    lang = serializers.CharField(required=False, allow_blank=True)
    timeZone = serializers.CharField(required=False, allow_blank=True)
    syncData = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        user = instance
        profile = getattr(user, "profile", None)

        # Update User fields
        if "name" in validated_data:
            name_parts = validated_data["name"].split(" ", 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
            else:
                user.last_name = ""

        if "email" in validated_data:
            user.email = validated_data["email"]

        user.save()

        # Update Profile fields
        if profile:
            if "title" in validated_data:
                profile.position = validated_data["title"]
            if "telephone" in validated_data:
                profile.telephone = validated_data["telephone"]
            if "avatar" in validated_data:
                profile.avatar = validated_data["avatar"]
            if "lang" in validated_data:
                profile.language = validated_data["lang"]
            if "timeZone" in validated_data:
                profile.timezone = validated_data["timeZone"]
            profile.save()

        return user
