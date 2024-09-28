from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('topics/', views.AllTopicsView.as_view(), name="all_topics"),

    path('create-room/', views.CreateRoomView.as_view(), name="create_room"),
    path('rooms/<int:pk>/edit', views.UpdateRoomView.as_view(), name="edit_room"),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name="room_detail"),
    path('rooms/<int:pk>/remove', views.DeleteRoomView.as_view(), name="delete_room"),
    path('messages/<int:pk>/remove',
         views.DeleteMessageView.as_view(), name="delete_message"),

    path('profile/<int:pk>', views.UserProfileView.as_view(), name="user_profile"),

    path('login/', views.LoginView.as_view(), name="login"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('logout/', view=LogoutView.as_view(), name="logout")
]
