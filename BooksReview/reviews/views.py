from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Ticket
from .forms import TicketForm


@login_required
def home(request):
    tickets = Ticket.objects.all()  # Récupère tous les tickets
    form = TicketForm()  # Formulaire pour créer un nouveau ticket

    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)  # Crée une instance sans la sauvegarder encore
            ticket.user = request.user  # Assigne l'utilisateur connecté
            ticket.save()
            return redirect('home')  # Redirige vers la page d'accueil après la création du ticket

    return render(request, 'reviews/home.html', {'tickets': tickets, 'form': form})

