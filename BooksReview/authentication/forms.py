from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username', 'email', 'first_name','last_name', 'role']

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Nom d’utilisateur', 'class': 'form-control'})
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-control'})
    )
    