from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import apiNotes
from .serializer import (
    RegisterSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    NoteSerializer,
)


class IndexView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'message': 'Welcome to the Notes App REST API',
            'endpoints': {
                'register': '/api/register/',
                'login': '/api/login/',
                'logout': '/api/logout/',
                'forgot_password': '/api/forgot-password/',
                'token_refresh': '/api/token/refresh/',
                'notes': '/api/notes/',
                'create_note': '/api/notes/create/',
                'edit_note': '/api/notes/edit/<int:note_id>/',
                'delete_note': '/api/notes/delete/<int:note_id>/',
            }
        })


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

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
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


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


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        user.set_password(password)
        user.save()

        return Response(
            {'message': 'Password updated successfully.'},
            status=status.HTTP_200_OK,
        )


# --- Notes CRUD Class-Based Views ---

class FetchNotesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notes = apiNotes.objects.filter(user=request.user).order_by('-updated_at')
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, note_id, user):
        return get_object_or_404(apiNotes, id=note_id, user=user)

    def get(self, request, note_id):
        note = self.get_object(note_id, request.user)
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, note_id):
        note = self.get_object(note_id, request.user)
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, note_id):
        note = self.get_object(note_id, request.user)
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteNoteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, note_id):
        note = get_object_or_404(apiNotes, id=note_id, user=request.user)
        note.delete()
        return Response({'message': 'Note deleted successfully.'}, status=status.HTTP_200_OK)
