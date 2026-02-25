from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('chatrooms/create/', views.create_chatroom, name='create_chatroom'),
    path('chatrooms/', views.list_chatrooms, name='list_chatrooms'),
]
