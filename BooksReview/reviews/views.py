from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
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
    return render(request, 'reviews/create-ticket.html', context=context)

@login_required
def view_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'reviews/display-tickets.html', {'ticket': ticket})


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.user != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier ce billet.")
    edit_form = forms.TicketForm(instance=ticket)
    delete_form = forms.DeleteTicketForm()
    if request.method == 'POST':
        if 'edit_ticket' in request.POST:
            edit_form = forms.TicketForm(request.POST, instance=ticket)
            if edit_form.is_valid():
                edit_form.save()
                return redirect('home')
        if 'delete_ticket' in request.POST:
            delete_form = forms.DeleteTicketForm(request.POST)
            if delete_form.is_valid():
                ticket.delete()
                return redirect('home')
    context = {
        'edit_form': edit_form,
        'delete_form': delete_form,
    }
    return render(request, 'reviews/edit-ticket.html', context=context)


@login_required
def create_review(request):
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        review_form = forms.ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('home')
    return render(request, 'reviews/create-review.html',{'review_form': review_form})