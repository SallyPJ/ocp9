from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class SignupForm(UserCreationForm):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Nom d’utilisateur', 'class': 'form-control '})
    )
    password1 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmez le mot de passe', 'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username']

    def clean_username(self):
        username = self.cleaned_data['username']
        return username.lower()


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Nom d’utilisateur', 'class': 'form-control form-control__larger'})
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-control form-control__larger'})
    )
