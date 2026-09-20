from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .models import apiNotes, EmailOTP
from .serializer import (
    RegisterSerializer,
    RegisterResponseSerializer,
    VerifyRegistrationSerializer,
    LoginSerializer,
    LogoutRequestSerializer,
    ForgotPasswordRequestSerializer,
    ForgotPasswordVerifySerializer,
    NoteSerializer,
    AuthSuccessSerializer,
    MessageResponseSerializer,
    ErrorResponseSerializer,
    DetailErrorResponseSerializer,
    PaginatedNoteResponseSerializer,
)
from django.core.cache import cache
from .utils import generate_otp, send_otp_email
from .pagination import NotesPagination


# --- Cache Helpers ---

def get_user_notes_cache_version(user_id: int) -> int:
    """Retrieve or initialize the cache version for the user's notes."""
    version_key = f"user_notes_version:{user_id}"
    version = cache.get(version_key)
    if version is None:
        version = 1
        cache.set(version_key, version, timeout=86400 * 30)  # 30 days
    return version


def invalidate_user_notes_cache(user_id: int) -> None:
    """Invalidate all cached note pages for the user."""
    version_key = f"user_notes_version:{user_id}"
    try:
        cache.incr(version_key)
    except Exception:
        current_v = cache.get(version_key, 1)
        cache.set(version_key, current_v + 1, timeout=86400 * 30)

    # If using django-redis backend, also purge matching keys directly
    if hasattr(cache, 'delete_pattern'):
        try:
            cache.delete_pattern(f"*user_notes:{user_id}:*")
        except Exception:
            pass


@extend_schema(
    summary="API Root / Overview",
    description="Returns a list and description of all available endpoints in the Notes App REST API.",
    tags=["General"],
    responses={
        200: OpenApiResponse(
            description="API overview and endpoint directory",
            examples=[
                OpenApiExample(
                    "Endpoints Directory Example",
                    value={
                        "message": "Welcome to the Notes App REST API",
                        "endpoints": {
                            "register": "/api/register/",
                            "verify_registration": "/api/verify-registration/",
                            "login": "/api/login/",
                            "logout": "/api/logout/",
                            "forgot_password_request": "/api/forgot-password/request/",
                            "forgot_password_verify": "/api/forgot-password/verify/",
                            "token_refresh": "/api/token/refresh/",
                            "notes": "/api/notes/",
                            "create_note": "/api/notes/create/",
                            "edit_note": "/api/notes/edit/<int:note_id>/",
                            "delete_note": "/api/notes/delete/<int:note_id>/",
                        }
                    }
                )
            ]
        )
    }
)
class IndexView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'message': 'Welcome to the Notes App REST API',
            'endpoints': {
                'register': '/api/register/',
                'verify_registration': '/api/verify-registration/',
                'login': '/api/login/',
                'logout': '/api/logout/',
                'forgot_password_request': '/api/forgot-password/request/',
                'forgot_password_verify': '/api/forgot-password/verify/',
                'token_refresh': '/api/token/refresh/',
                'notes': '/api/notes/',
                'create_note': '/api/notes/create/',
                'edit_note': '/api/notes/edit/<int:note_id>/',
                'delete_note': '/api/notes/delete/<int:note_id>/',
            }
        })


@extend_schema(
    summary="Register a new user",
    description=(
        "Registers a new account with `username`, `email`, and `password`.\n\n"
        "**Workflow**:\n"
        "1. The account is created with `is_active=False`.\n"
        "2. A cryptographically secure 6-digit OTP is generated and emailed to the user.\n"
        "3. Submit the OTP to `/api/verify-registration/` to activate the account."
    ),
    tags=["Authentication"],
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(
            response=RegisterResponseSerializer,
            description="User registered successfully. OTP sent to email."
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Validation error: duplicate username, duplicate email, or missing required fields."
        ),
    }
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            EmailOTP.objects.filter(email=user.email, purpose='registration', is_used=False).update(is_used=True)

            otp = generate_otp()
            EmailOTP.objects.create(email=user.email, otp=otp, purpose='registration')
            send_otp_email(user.email, otp, 'registration')

            return Response({
                'message': 'Registration successful. An OTP has been sent to your email to verify your account.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Verify registration OTP & activate account",
    description=(
        "Verifies the 6-digit OTP sent to the user's email during registration.\n\n"
        "**Workflow**:\n"
        "1. Validates the OTP against the database and checks the 10-minute expiration.\n"
        "2. Activates the account (`is_active=True`).\n"
        "3. Marks the OTP as used.\n"
        "4. Returns JWT `access` and `refresh` tokens for immediate login."
    ),
    tags=["Authentication"],
    request=VerifyRegistrationSerializer,
    responses={
        200: OpenApiResponse(
            response=AuthSuccessSerializer,
            description="Account activated successfully; JWT tokens returned."
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid or expired OTP code."
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="User associated with this email not found."
        ),
    }
)
class VerifyRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'].lower()
        otp = serializer.validated_data['otp']

        otp_record = (
            EmailOTP.objects.filter(email=email, purpose='registration', is_used=False)
            .order_by('-created_at')
            .first()
        )

        if not otp_record or otp_record.otp != otp or not otp_record.is_valid():
            return Response(
                {'error': 'Invalid or expired OTP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response(
                {'error': 'User associated with this email not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.is_active = True
        user.save()

        otp_record.is_used = True
        otp_record.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Account verified successfully.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Log in user",
    description=(
        "Authenticates username and password and returns JWT access & refresh tokens.\n\n"
        "**Error Codes**:\n"
        "- `400 Bad Request`: Missing username or password.\n"
        "- `401 Unauthorized`: Invalid credentials.\n"
        "- `403 Forbidden`: Account is inactive/unverified. User must complete OTP verification."
    ),
    tags=["Authentication"],
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            response=AuthSuccessSerializer,
            description="Login successful; returns user info and JWT access & refresh tokens."
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad request: missing username or password."
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized: invalid username or password."
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden: account not verified via OTP."
        ),
    }
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user_obj = User.objects.filter(username=username).first()
        if user_obj and user_obj.check_password(password) and not user_obj.is_active:
            return Response(
                {'error': 'Account not verified. Please verify your account using the OTP sent to your email.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = authenticate(request=request, username=username, password=password)
        if user is None:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


@extend_schema(
    summary="Log out user",
    description=(
        "Blacklists the provided refresh token so it cannot be used again.\n\n"
        "**Headers Required**:\n"
        "```http\n"
        "Authorization: Bearer <your_access_token>\n"
        "```\n"
        "**Body Required**:\n"
        "`{\"refresh\": \"<refresh_token>\"}`"
    ),
    tags=["Authentication"],
    request=LogoutRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=MessageResponseSerializer,
            description="Logout successful; refresh token blacklisted."
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad request: missing or invalid/expired refresh token."
        ),
        401: OpenApiResponse(
            response=DetailErrorResponseSerializer,
            description="Unauthorized: missing or invalid Bearer access token."
        ),
    }
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful.'})
        except Exception:
            return Response(
                {'error': 'Invalid or expired refresh token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(
    summary="Request password reset OTP",
    description=(
        "Sends a 6-digit password reset OTP to the user's registered email.\n\n"
        "The code is valid for 10 minutes. Submit it with your new password to `/api/forgot-password/verify/`."
    ),
    tags=["Password Reset"],
    request=ForgotPasswordRequestSerializer,
    responses={
        200: OpenApiResponse(
            response=MessageResponseSerializer,
            description="Password reset OTP sent to email."
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad request: invalid email format."
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not found: no active account found with this email."
        ),
    }
)
class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'].lower()
        user = User.objects.filter(email__iexact=email, is_active=True).first()

        if not user:
            return Response(
                {'error': 'No active account found with this email address.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        EmailOTP.objects.filter(email=email, purpose='forgot_password', is_used=False).update(is_used=True)

        otp = generate_otp()
        EmailOTP.objects.create(email=email, otp=otp, purpose='forgot_password')
        send_otp_email(email, otp, 'forgot_password')

        return Response({
            'message': 'Password reset OTP has been sent to your email.',
            'email': email,
        }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Verify reset OTP & set new password",
    description=(
        "Verifies the password reset OTP and sets the new password for the account.\n\n"
        "Once updated, the user can immediately log in with their new password."
    ),
    tags=["Password Reset"],
    request=ForgotPasswordVerifySerializer,
    responses={
        200: OpenApiResponse(
            response=MessageResponseSerializer,
            description="Password reset successfully. User can now log in."
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad request: invalid or expired OTP, or validation error."
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not found: user not found."
        ),
    }
)
class ForgotPasswordVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'].lower()
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['password']

        otp_record = (
            EmailOTP.objects.filter(email=email, purpose='forgot_password', is_used=False)
            .order_by('-created_at')
            .first()
        )

        if not otp_record or otp_record.otp != otp or not otp_record.is_valid():
            return Response(
                {'error': 'Invalid or expired OTP.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.set_password(new_password)
        user.save()

        otp_record.is_used = True
        otp_record.save()

        return Response({
            'message': 'Password reset successfully. You can now log in with your new password.'
        }, status=status.HTTP_200_OK)



@extend_schema(
    summary="Fetch all user notes (paginated)",
    description=(
        "Retrieves a paginated list of all notes created by the currently authenticated user, "
        "ordered by most recently updated first.\n\n"
        "**Query Parameters**:\n"
        "- `page` (optional): Page number (default: 1)\n"
        "- `page_size` (optional): Number of notes per page (default: 10, max: 100)\n\n"
        "Requires Bearer token authentication in the `Authorization` header."
    ),
    tags=["Notes CRUD"],
    responses={
        200: OpenApiResponse(
            response=PaginatedNoteResponseSerializer,
            description="Paginated list of notes with count, next, previous links, and results."
        ),
        401: OpenApiResponse(
            response=DetailErrorResponseSerializer,
            description="Unauthorized: missing or invalid Bearer token."
        ),
    }
)
class FetchNotesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = NotesPagination

    def get(self, request):
        page = request.query_params.get('page', '1')
        page_size = request.query_params.get('page_size', '10')

        # 1. Check cache first (Cache-Aside pattern)
        cache_version = get_user_notes_cache_version(request.user.id)
        cache_key = f"user_notes:{request.user.id}:v_{cache_version}:p_{page}:s_{page_size}"

        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response, status=status.HTTP_200_OK)

        # 2. Cache miss: Query database
        notes = apiNotes.objects.filter(user=request.user).order_by('-updated_at')
        paginator = self.pagination_class()
        page_obj = paginator.paginate_queryset(notes, request, view=self)
        if page_obj is not None:
            serializer = NoteSerializer(page_obj, many=True)
            response_data = paginator.get_paginated_response(serializer.data).data
            # Cache for 10 minutes (600 seconds)
            cache.set(cache_key, response_data, timeout=600)
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = NoteSerializer(notes, many=True)
        response_data = serializer.data
        cache.set(cache_key, response_data, timeout=600)
        return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Create a new note",
    description=(
        "Creates a new note linked to the authenticated user.\n\n"
        "- `title`: Required (max 200 characters)\n"
        "- `content`: Required text\n"
        "- `image_url`: Optional image URL\n\n"
        "Requires Bearer token authentication."
    ),
    tags=["Notes CRUD"],
    request=NoteSerializer,
    responses={
        201: OpenApiResponse(
            response=NoteSerializer,
            description="Note created successfully."
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad request: missing title or content."
        ),
        401: OpenApiResponse(
            response=DetailErrorResponseSerializer,
            description="Unauthorized: missing or invalid Bearer token."
        ),
    }
)
class CreateNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            # Invalidate cached notes for this user
            invalidate_user_notes_cache(request.user.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, note_id, user):
        return get_object_or_404(apiNotes, id=note_id, user=user)

    @extend_schema(
        summary="Get single note detail",
        description=(
            "Retrieves details for a single note by ID.\n\n"
            "Verifies that the note belongs to the currently authenticated user."
        ),
        tags=["Notes CRUD"],
        responses={
            200: NoteSerializer,
            401: OpenApiResponse(
                response=DetailErrorResponseSerializer,
                description="Unauthorized: missing or invalid Bearer token."
            ),
            404: OpenApiResponse(
                response=DetailErrorResponseSerializer,
                description="Not found: note does not exist or belongs to another user."
            ),
        }
    )
    def get(self, request, note_id):
        note = self.get_object(note_id, request.user)
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update note (full update)",
        description=(
            "Completely updates all fields of a note owned by the authenticated user.\n\n"
            "Both `title` and `content` are required."
        ),
        tags=["Notes CRUD"],
        request=NoteSerializer,
        responses={
            200: OpenApiResponse(
                response=NoteSerializer,
                description="Note updated successfully."
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad request: validation error on fields."
            ),
            401: OpenApiResponse(
                response=DetailErrorResponseSerializer,
                description="Unauthorized: missing or invalid Bearer token."
            ),
            404: OpenApiResponse(
                response=DetailErrorResponseSerializer,
                description="Not found: note does not exist or belongs to another user."
            ),
        }
    )
    def put(self, request, note_id):
        note = self.get_object(note_id, request.user)
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            invalidate_user_notes_cache(request.user.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update note (partial update)",
        description=(
            "Partially updates specific fields (`title`, `content`, or `image_url`) "
            "of a note owned by the authenticated user."
        ),
        tags=["Notes CRUD"],
        request=NoteSerializer,
        responses={
            200: OpenApiResponse(
                response=NoteSerializer,
                description="Note updated successfully."
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad request: validation error on fields."
            ),
            401: OpenApiResponse(
                response=DetailErrorResponseSerializer,
                description="Unauthorized: missing or invalid Bearer token."
            ),
            404: OpenApiResponse(
                response=DetailErrorResponseSerializer,
                description="Not found: note does not exist or belongs to another user."
            ),
        }
    )
    def patch(self, request, note_id):
        note = self.get_object(note_id, request.user)
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            invalidate_user_notes_cache(request.user.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Delete a note",
    description=(
        "Deletes a note by ID, verifying that the note belongs to the authenticated user."
    ),
    tags=["Notes CRUD"],
    responses={
        200: OpenApiResponse(
            response=MessageResponseSerializer,
            description="Note deleted successfully."
        ),
        401: OpenApiResponse(
            response=DetailErrorResponseSerializer,
            description="Unauthorized: missing or invalid Bearer token."
        ),
        404: OpenApiResponse(
            response=DetailErrorResponseSerializer,
            description="Not found: note does not exist or belongs to another user."
        ),
    }
)
class DeleteNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, note_id):
        note = get_object_or_404(apiNotes, id=note_id, user=request.user)
        note.delete()
        invalidate_user_notes_cache(request.user.id)
        return Response({'message': 'Note deleted successfully.'}, status=status.HTTP_200_OK)
