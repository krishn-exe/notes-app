from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from .models import apiNotes
from .serializer import RegisterSerializer, LoginSerializer, NoteSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
    return Response({
        'message': 'Welcome to the Notes App REST API',
        'endpoints': {
            'register': '/api/register/',
            'login': '/api/login/',
            'logout': '/api/logout/',
            'token_refresh': '/api/token/refresh/',
            'notes': '/api/notes/',
            'create_note': '/api/notes/create/',
            'edit_note': '/api/notes/edit/<int:note_id>/',
            'delete_note': '/api/notes/delete/<int:note_id>/',
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
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


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FetchNotes(request):
    notes = apiNotes.objects.filter(user=request.user).order_by('-updated_at')
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def CreateNote(request):
    serializer = NoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PATCH'])
@permission_classes([IsAuthenticated])
def EditNote(request, note_id):
    note = get_object_or_404(apiNotes, id=note_id, user=request.user)

    if request.method == 'GET':
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

    partial = (request.method == 'PATCH')
    serializer = NoteSerializer(note, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def DeleteNote(request, note_id):
    note = get_object_or_404(apiNotes, id=note_id, user=request.user)
    note.delete()
    return Response({'message': 'Note deleted successfully.'}, status=status.HTTP_200_OK)