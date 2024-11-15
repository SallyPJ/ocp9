from django import forms
from .models import Ticket, Photo


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description']

class PhotoForm(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = ['image', caption]