from typing import Any
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View, FormView, CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from chatrooms.forms import LoginForm, RegisterForm, RoomForm
from chatrooms.models import Room, Topic

# Create your views here.


class HomeView(View):
    def get(self, request: HttpRequest):
        return HttpResponse("Homepage")


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
