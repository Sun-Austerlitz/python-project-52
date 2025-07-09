from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, label="Имя")
    last_name = forms.CharField(max_length=150, required=True, label="Фамилия")

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]
