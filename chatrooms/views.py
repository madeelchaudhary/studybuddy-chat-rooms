from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View, FormView, CreateView, UpdateView, ListView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count

from chatrooms.forms import LoginForm, RegisterForm, RoomForm
from chatrooms.models import Message, Room, Topic

# Create your views here.


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
