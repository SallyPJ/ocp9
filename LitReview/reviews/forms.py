from django import forms
from .models import Ticket, Photo, Review
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class TicketForm(forms.ModelForm):
    edit_ticket = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=True)
    class Meta:
        model = Ticket
        fields = ['title', 'description']
        labels = {
            'title': '',
            'description': '',
        }
        fieldsets = ()
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control ',
                                            'placeholder': 'Entrez le titre'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control__description',
                                                 'placeholder': 'Entrez la description'}),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']
        labels = {
            'image': '',
        }
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'aria-label': 'Téléchargez une image',

                                                     }),
        }



class DeleteTicketForm(forms.Form):
    delete_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'headline', 'body']
        labels = {
            'headline': '',
            'body': '',
        }
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control ',
                                            'placeholder': 'Entrez le titre'}),
            'body': forms.Textarea(attrs={'class': 'form-control form-control__description',
                                                 'placeholder': 'Entrez la description'}),
            'rating': forms.RadioSelect(choices=[
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3'),
                ('4', '4'),
                ('5', '5'),
            ],
                attrs={
                    'class': 'form-control__checkbox',
                },
            ),
        }


User = get_user_model()


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

        # Vérifier que l'utilisateur existe
        try:
            followed_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("Cet utilisateur n'existe pas.")

        # Empêcher de se suivre soi-même
        if self.user and followed_user == self.user:
            raise ValidationError("Vous ne pouvez pas vous suivre vous-même.")

        return followed_user  # Retourne l'objet User, pas une chaîne