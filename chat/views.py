from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer
from .models import Chatroom, ChatroomMember


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'display_name': user.userprofile.display_name
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username and password:
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'display_name': user.userprofile.display_name
                },
                'token': token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        'error': 'Username and password required'
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_chatroom(request):
    name = request.data.get('name')
    description = request.data.get('description', '')
    is_private = request.data.get('is_private', False)
    
    if not name:
        return Response({
            'error': 'Name is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        chatroom = Chatroom.objects.create(
            name=name,
            description=description,
            is_private=is_private,
            created_by=request.user
        )
        
        ChatroomMember.objects.create(
            user=request.user,
            chatroom=chatroom,
            role='admin'
        )
        
        return Response({
            'id': chatroom.id,
            'name': chatroom.name,
            'description': chatroom.description,
            'created_by': chatroom.created_by.username
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    try:
        # Delete the user's token to invalidate the session
        Token.objects.get(user=request.user).delete()
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
