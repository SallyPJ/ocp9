from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class FollowUsersForm(forms.Form):
    followed_username = forms.CharField(
        label='',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur',
                                      'class': 'form-control form-control__searchbar'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Récupérer l'utilisateur connecté
        super().__init__(*args, **kwargs)

    def clean_followed_username(self):
        username = self.cleaned_data['followed_username']

        # Récupérer le modèle utilisateur
        User = get_user_model()

        # Vérifier que l'utilisateur existe
        try:
            followed_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("Cet utilisateur n'existe pas.")

        # Empêcher de se suivre soi-même
        if self.user and followed_user == self.user:
            raise ValidationError("Vous ne pouvez pas vous suivre vous-même.")

        return followed_user  # Retourne l'objet User, pas une chaîne