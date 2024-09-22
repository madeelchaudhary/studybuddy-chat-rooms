from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import View, FormView
from django.contrib.auth import authenticate, login
from django.contrib import messages

from chatrooms.forms import LoginForm, RegisterForm

# Create your views here.


class HomeView(View):
    def get(self, request: HttpRequest):
        return HttpResponse("Homepage")


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
