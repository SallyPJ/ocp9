from django import forms
from .models import Ticket, Photo


class TicketForm(forms.ModelForm):
    edit_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)
    class Meta:
        model = Ticket
        fields = ['title', 'description']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'caption']

class DeleteTicketForm(forms.Form):
    delete_ticket = forms.BooleanField(widget=forms.HiddenInput, initial=True)