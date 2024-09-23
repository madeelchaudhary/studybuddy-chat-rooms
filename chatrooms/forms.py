from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import Room

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True,)
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'autocomplete': 'password'}))


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['created_at', 'updated_at', 'topic', 'participants']

    topic_input = forms.CharField(max_length=200, strip=True, required=True, min_length=2)
