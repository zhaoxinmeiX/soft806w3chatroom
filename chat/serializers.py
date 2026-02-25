from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    display_name = serializers.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'display_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        display_name = validated_data.pop('display_name')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        
        UserProfile.objects.create(
            user=user,
            display_name=display_name
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'display_name', 'bio', 'is_online', 'last_seen', 'created_at']
        read_only_fields = ['is_online', 'last_seen', 'created_at']
