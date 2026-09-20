from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from .models import apiNotes

# Regex Validators for Serializer Validation
username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_]{3,30}$',
    message='Username must be 3-30 characters long and contain only letters, numbers, and underscores.'
)

password_validator = RegexValidator(
    regex=r'^(?=.*[A-Za-z])(?=.*\d).{8,}$',
    message='Password must be at least 8 characters long and contain at least one letter and one number.'
)

otp_validator = RegexValidator(
    regex=r'^\d{6}$',
    message='OTP must be exactly 6 digits.'
)


# --- Request Serializers ---

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Registration request",
            value={
                "username": "alice",
                "email": "alice@example.com",
                "password": "Password123",
            },
            request_only=True,
        )
    ]
)
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[username_validator],
        help_text="Username (3-30 characters: letters, numbers, and underscores)."
    )
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        validators=[password_validator],
        help_text="Password (min 8 chars, at least one letter and one number)."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,
        )
        return user


class VerifyRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="The email address provided during registration."
    )
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        validators=[otp_validator],
        help_text="The 6-digit verification code received via email."
    )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Your registered username.")
    password = serializers.CharField(required=True, write_only=True, help_text="Your account password.")


class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True,
        help_text="The refresh token to be blacklisted."
    )


class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="The email address associated with your account."
    )


class ForgotPasswordVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        help_text="The email address associated with your account."
    )
    otp = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        validators=[otp_validator],
        help_text="The 6-digit password reset code received via email."
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[password_validator],
        help_text="Your new password (min 8 chars, at least one letter and one number)."
    )


class NoteSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default='',
        help_text="Optional URL of an attached image."
    )

    class Meta:
        model = apiNotes
        fields = ['id', 'title', 'content', 'image_url', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True, help_text="User ID")
    username = serializers.CharField(read_only=True, help_text="Username")
    email = serializers.EmailField(read_only=True, help_text="Email address")


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True, help_text="JWT Access Token (send in Authorization header)")
    refresh = serializers.CharField(read_only=True, help_text="JWT Refresh Token (use to obtain new access tokens)")


class RegisterResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
    user = UserProfileSerializer(read_only=True)


class AuthSuccessSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
    user = UserProfileSerializer(read_only=True)
    tokens = TokenPairSerializer(read_only=True)


class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True, help_text="Status message")


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(read_only=True, help_text="Error description")


class DetailErrorResponseSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True, help_text="Authentication or permission error detail")
