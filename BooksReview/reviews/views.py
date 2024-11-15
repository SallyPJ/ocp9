from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket, Photo
from .forms import TicketForm
from . import forms


@login_required
def home(request):
    tickets = Ticket.objects.all()  # Récupère tous les tickets
    photos = Photo.objects.all()
    #form = TicketForm()  # Formulaire pour créer un nouveau ticket

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)  # Crée une instance sans la sauvegarder encore
            ticket.user = request.user  # Assigne l'utilisateur connecté
            ticket.save()
            return redirect('home')  # Redirige vers la page d'accueil après la création du ticket

    return render(request, 'reviews/home.html', {'tickets': tickets,'photos': photos})
#'form': form}

# blog/views.py
@login_required
def ticket_and_photo_upload(request):
    ticket_form = forms.TicketForm()
    photo_form = forms.PhotoForm()
    if request.method == 'POST':
        ticket_form = forms.TicketForm(request.POST)
        photo_form = forms.PhotoForm(request.POST, request.FILES)
        if all([ticket_form.is_valid(), photo_form.is_valid()]):
            photo = photo_form.save(commit=False)
            photo.uploader = request.user
            photo.save()
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.photo = photo
            ticket.save()
            return redirect('home')
    context = {
        'ticket_form': ticket_form,
        'photo_form': photo_form,
}
    return render(request, 'reviews/create-post.html', context=context)

# blog/views.py


@login_required
def view_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'reviews/view_reviews.html', {'ticket': ticket})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    edit_form = forms.TicketForm(instance=ticket)
    delete_form = forms.DeleteTicketForm()
    if request.method == 'POST':
        if 'edit_blog' in request.POST:
            edit_form = forms.TicketForm(request.POST, instance=ticket)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('home')
            if 'delete_blog' in request.POST:
                delete_form = forms.DeleteTicketForm(request.POST)
                if delete_form.is_valid():
                    ticket.delete()
                    return redirect('home')
    context = {
        'edit_form': edit_form,
        'delete_form': delete_form,
}
    return render(request, 'blog/edit_ticket.html', context=context)