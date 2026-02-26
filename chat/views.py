from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, ChatroomSerializer, MessageSerializer, UserProfileSerializer
from .models import Chatroom, ChatroomMember, Message, UserProfile


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


class ChatroomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_chatrooms(request):
    chatrooms = Chatroom.objects.filter(is_private=False).order_by('-created_at')
    
    paginator = ChatroomPagination()
    paginated_chatrooms = paginator.paginate_queryset(chatrooms, request)
    
    serializer = ChatroomSerializer(paginated_chatrooms, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_chatroom(request, chatroom_id):
    try:
        chatroom = Chatroom.objects.get(id=chatroom_id)
    except Chatroom.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if chatroom.is_private:
        return Response({
            'error': 'Cannot join private chatroom'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if ChatroomMember.objects.filter(user=request.user, chatroom=chatroom).exists():
        return Response({
            'error': 'You are already a member'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    ChatroomMember.objects.create(
        user=request.user,
        chatroom=chatroom,
        role='member'
    )
    
    return Response({
        'message': 'Successfully joined chatroom'
    }, status=status.HTTP_200_OK)


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def message_history(request, chatroom_id):
    # Check if chatroom exists
    try:
        chatroom = Chatroom.objects.get(id=chatroom_id)
    except Chatroom.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is a member of the chatroom
    if not ChatroomMember.objects.filter(user=request.user, chatroom=chatroom).exists():
        return Response({
            'error': 'You are not a member of this chatroom'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Filter messages by room_id, order by created_at descending, use select_related
    messages = Message.objects.filter(
        chatroom=chatroom
    ).select_related('sender').order_by('-created_at')
    
    # Apply pagination
    paginator = MessagePagination()
    paginated_messages = paginator.paginate_queryset(messages, request)
    
    # Serialize the messages
    serializer = MessageSerializer(paginated_messages, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request, chatroom_id):
    # Check if chatroom exists
    try:
        chatroom = Chatroom.objects.get(id=chatroom_id)
    except Chatroom.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user is a member of the chatroom
    if not ChatroomMember.objects.filter(user=request.user, chatroom=chatroom).exists():
        return Response({
            'error': 'You are not a member of this chatroom'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Validate request body contains content field
    content = request.data.get('content')
    if not content:
        return Response({
            'error': 'Content field is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create new message
    message = Message.objects.create(
        chatroom=chatroom,
        sender=request.user,
        content=content
    )
    
    # Return response with message details
    serializer = MessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    try:
        user_profile = request.user.userprofile
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chatroom_details(request, room_id):
    try:
        chatroom = Chatroom.objects.get(id=room_id)
        serializer = ChatroomSerializer(chatroom)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Chatroom.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    try:
        user_profile = request.user.userprofile
        
        # Get display_name from request body
        display_name = request.data.get('display_name')
        
        if display_name is None:
            return Response({
                'error': 'display_name field is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate display_name length
        if len(display_name.strip()) == 0:
            return Response({
                'error': 'display_name cannot be empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(display_name) > 100:
            return Response({
                'error': 'display_name cannot exceed 100 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the display_name field
        user_profile.display_name = display_name.strip()
        user_profile.save()
        
        # Return updated user data
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
