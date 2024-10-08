from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import View, FormView, CreateView, UpdateView, ListView, DetailView, DeleteView
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count

from chatrooms.forms import LoginForm, RegisterForm, RoomForm
from chatrooms.models import Message, Room, Topic

# Create your views here.
User = get_user_model()


class HomeView(ListView):
    model = Room
    template_name = "chatrooms/home.html"
    context_object_name = "rooms"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        q = self.request.GET.get('q') if self.request.GET.get('q') else ''

        return queryset.filter(Q(name__icontains=q) | Q(topic__name__icontains=q)).annotate(participant_count=Count('participants')).select_related('topic').select_related('host')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.annotate(
            room_count=Count('rooms')).order_by('-room_count')[:6]
        context['topic_count'] = Topic.objects.all().count()
        context['recent_messages'] = Message.objects.all().select_related(
            'user').select_related('room').order_by('-created_at')[:6]
        return context


class AllTopicsView(ListView):
    model = Topic
    template_name = "chatrooms/all_topics.html"
    context_object_name = "topics"

    def get_queryset(self) -> QuerySet[Any]:
        q = self.request.GET.get('q') if self.request.GET.get('q') else ''
        queryset = super().get_queryset()

        return queryset.filter(Q(name__icontains=q)).annotate(room_count=Count('rooms'))


class CreateRoomView(LoginRequiredMixin, CreateView):
    login_url = "/login"
    raise_exception = False

    form_class = RoomForm
    template_name = "chatrooms/create_room.html"
    success_url = "/"
    model = Room

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        return context

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        data = form.cleaned_data

        topic, created = Topic.objects.get_or_create(
            name=data.get('topic_input'))
        room = form.save(commit=False)
        room.topic = topic
        room.save()
        return redirect('home')


class UpdateRoomView(LoginRequiredMixin, UpdateView):
    login_url = "/login"
    raise_exception = False

    form_class = RoomForm
    template_name = "chatrooms/update_room.html"
    success_url = "/"
    model = Room

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        return context

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        room = self.get_object()
        if room.host != request.user:
            raise Http404()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        room = self.get_object()
        if room.host != request.user:
            raise Http404()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        data = form.cleaned_data
        topic, created = Topic.objects.get_or_create(
            name=data.get('topic_input'))
        room = form.save(commit=False)
        room.topic = topic
        room.host = self.request.user
        room.save()
        return redirect('home')


class RoomDetailView(DetailView):
    template_name = "chatrooms/room_detail.html"
    model = Room
    context_object_name = "room"

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().select_related('host')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['room_messages'] = Message.objects.filter(
            room=self.object).select_related('user').order_by('created_at')
        context['participants'] = self.object.participants.all()
        context['participant_count'] = self.object.participants.count()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        room = self.get_object()
        content = request.POST.get('content')
        if content:
            room.participants.add(request.user)
            Message.objects.create(
                room=room, user=request.user, content=content)
        return self.get(request, *args, **kwargs)


class DeleteRoomView(LoginRequiredMixin, DeleteView):
    login_url = "/login"
    raise_exception = False

    template_name = "chatrooms/delete.html"
    model = Room
    context_object_name = "object"
    success_url = "/"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        room = self.get_object()
        if request.user != room.host:
            raise Http404()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        room = self.get_object()
        if request.user != room.host:
            raise Http404()
        return super().post(request, *args, **kwargs)


class DeleteMessageView(LoginRequiredMixin, DeleteView):
    login_url = "/login"
    raise_exception = False

    template_name = "chatrooms/delete.html"
    model = Message
    context_object_name = "object"
    success_url = "/"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        message = self.get_object()
        if request.user != message.user:
            raise Http404()
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        message = self.get_object()
        if request.user != message.user:
            raise Http404()
        return super().post(request, *args, **kwargs)


class UserProfileView(DetailView):
    template_name = 'chatrooms/user_profile.html'
    model = User
    context_object_name = 'user'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.object

        context['rooms'] = user.rooms.all().annotate(participant_count=Count(
            'participants')).select_related('topic').select_related('host')
        context['topics'] = Topic.objects.annotate(
            room_count=Count('rooms')).order_by('-room_count')[:6]
        context['topic_count'] = Topic.objects.all().count()
        context['recent_messages'] = Message.objects.filter(
            user=user).select_related('user').select_related('room').order_by('-created_at')[:6]

        return context


class LoginView(FormView):
    form_class = LoginForm
    template_name = "chatrooms/login.html"
    success_url = '/'

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect('home')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form: Any) -> HttpResponse:
        user = authenticate(request=self.request, **form.cleaned_data)

        if user:
            login(request=self.request, user=user)
            return super().form_valid(form)
        else:
            messages.error(request=self.request,
                           message="Either username or password is incorrect")

        return super().form_invalid(form)


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'chatrooms/register.html'
    success_url = "/login"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect('home')

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()

        return super().form_valid(form)
