from django.contrib import admin
from .models import UserProfile, Chatroom, ChatroomMember, Message


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'bio', 'is_online', 'last_seen', 'created_at')
    list_filter = ('is_online', 'created_at')
    search_fields = ('user__username', 'display_name')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Chatroom)
class ChatroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_private', 'get_member_count', 'created_at')
    list_filter = ('is_private', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ChatroomMember)
class ChatroomMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'chatroom', 'role', 'joined_at', 'is_muted', 'is_banned')
    list_filter = ('role', 'is_muted', 'is_banned', 'joined_at')
    search_fields = ('user__username', 'chatroom__name')
    readonly_fields = ('joined_at',)
    ordering = ('-joined_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chatroom', 'message_type', 'content_preview', 'is_edited', 'created_at')
    list_filter = ('message_type', 'is_edited', 'created_at')
    search_fields = ('sender__username', 'chatroom__name', 'content')
    readonly_fields = ('created_at', 'updated_at', 'edited_at')
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
