
from django.urls import path
from . import views


urlpatterns = [

    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),

    path('', views.home, name='home' ),
    path('room/<str:pk>', views.room, name='room' ),
    path('user/<str:pk>', views.userProfile, name="user-profile"),

    path('create/', views.createRoom, name='create-room'),
    path('update/<str:pk>', views.updateRoom, name='update-room'),
    path('delete/<str:pk>', views.deleteRoom, name='delete-room'),

    path('delete-message/<str:pk>', views.deleteMessage, name='delete-message'),
    path('update-user/', views.updateUser, name='update-user'),

]