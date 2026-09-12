from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Password"}))
