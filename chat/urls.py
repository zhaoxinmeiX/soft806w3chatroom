from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('chatrooms/create/', views.create_chatroom, name='create_chatroom'),
    path('chatrooms/', views.list_chatrooms, name='list_chatrooms'),
    path('chatrooms/<int:room_id>/', views.chatroom_details, name='chatroom_details'),
    path('chatrooms/<int:chatroom_id>/join/', views.join_chatroom, name='join_chatroom'),
    path('chatrooms/<int:chatroom_id>/messages/', views.message_history, name='message_history'),
    path('chatrooms/<int:chatroom_id>/send-message/', views.send_message, name='send_message'),
]
