from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('topics/', views.AllTopicsView.as_view(), name="all_topics"),
    path('create-room/', views.CreateRoomView.as_view(), name="create_room"),
    path('rooms/<int:pk>/edit', views.UpdateRoomView.as_view(), name="edit_room"),

    path('login/', views.LoginView.as_view(), name="login"),
    path('register/', views.RegisterView.as_view(), name="register")
]
