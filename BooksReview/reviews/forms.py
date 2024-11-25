from django import forms
from .models import Ticket, Photo, Review
from django.contrib.auth import get_user_model


class TicketForm(forms.ModelForm):
    edit_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)
    class Meta:
        model = Ticket
        fields = ['title', 'description']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']



class DeleteTicketForm(forms.Form):
    delete_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'headline', 'body']
        widgets = {
            'rating': forms.RadioSelect(choices=[
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3'),
                ('4', '4'),
                ('5', '5'),
            ]),
        }


User = get_user_model()


class FollowUsersForm(forms.Form):
    followed_user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Utilisateur à suivre",
        widget=forms.Select
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Récupérer l'utilisateur connecté
        super().__init__(*args, **kwargs)
        if user:
            # Exclure l'utilisateur connecté pour éviter de se suivre soi-même
            self.fields['followed_user'].queryset = User.objects.exclude(id=user.id)