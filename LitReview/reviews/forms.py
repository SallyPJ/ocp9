from django import forms
from .models import Ticket, Photo, Review


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


