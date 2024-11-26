from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Ticket, Photo, Review, UserFollows
from .forms import FollowUsersForm
from . import forms
from itertools import chain



@login_required
def home(request):
    followed_users = request.user.following.values_list('followed_user', flat=True)
    # Récupère tous les tickets avec leurs critiques associées
    tickets = Ticket.objects.filter(
        Q(user__in=followed_users) | Q(user=request.user)
    ).prefetch_related('review_set')

    # Récupère toutes les critiques avec leur ticket lié
    reviews = Review.objects.filter(
        Q(user__in=followed_users) | Q(user=request.user)
    ).select_related('ticket')

    posts = sorted(chain(tickets, reviews),
                   key=lambda instance: instance.time_created,
                   reverse=True)
    print("Tickets :", list(tickets))
    print("Reviews :", list(reviews))
    print("Posts combinés :", posts)
    context = {
        'posts': posts,
        }
    # Transmet les données au template
    return render(request, 'reviews/home.html', context=context)


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
                return redirect('posts')
        if 'delete_ticket' in request.POST:
            delete_form = forms.DeleteTicketForm(request.POST)
            if delete_form.is_valid():
                ticket.delete()
                return redirect('posts')
    context = {
        'edit_form': edit_form,
        'delete_form': delete_form,
    }
    return render(request, 'reviews/edit-ticket.html', context=context)


@login_required
def create_review(request,ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    review_form = forms.ReviewForm()
    if request.method == 'POST':
        review_form = forms.ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('home')

    context = {
        'review_form': review_form,
        'ticket': ticket,
    }
    return render(request, 'reviews/create-review.html', context=context)

@login_required
def create_ticket_and_review(request):
    ticket_form = forms.TicketForm()
    photo_form = forms.PhotoForm()
    review_form = forms.ReviewForm()

    if request.method == 'POST':
        ticket_form = forms.TicketForm(request.POST)
        photo_form = forms.PhotoForm(request.POST, request.FILES)
        review_form = forms.ReviewForm(request.POST)
        if all([ticket_form.is_valid(), photo_form.is_valid(), review_form.is_valid()]):
            # Sauvegarde du ticket
            photo = photo_form.save(commit=False)
            photo.uploader = request.user
            photo.save()
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.photo = photo
            ticket.save()

            # Sauvegarde de la critique liée au ticket
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()

            return redirect('home')
        else:
            # Afficher les erreurs de validation pour débogage
            print("Erreurs dans ticket_form :", ticket_form.errors)
            print("Erreurs dans photo_form :", photo_form.errors)
            # Redirige vers la page principale après succès

    context = {
        'ticket_form': ticket_form,
        'photo_form': photo_form,
        'review_form': review_form,
    }
    return render(request, 'reviews/create-ticket-and-review.html', context=context)



@login_required()
def display_user_posts(request):
    # Récupérer les tickets de l'utilisateur
    user_tickets = Ticket.objects.filter(user=request.user).prefetch_related('review_set')

    # Récupérer les critiques de l'utilisateur
    user_reviews = Review.objects.filter(user=request.user).select_related('ticket')

    # Fusionner et trier les tickets et critiques par date
    posts = sorted(
        chain(user_tickets, user_reviews),
        key=lambda instance: instance.time_created,
        reverse=True
    )

    return render(request, 'reviews/posts.html', {'posts': posts, 'show_buttons': True})

@login_required
def follow_users_form(request):
    if request.method == 'POST':
        if 'follow_user' in request.POST:  # Suivre un utilisateur
            form = FollowUsersForm(request.POST, user=request.user)
            if form.is_valid():
                followed_user = form.cleaned_data['followed_username']  # Utilise le bon champ
                UserFollows.objects.get_or_create(user=request.user, followed_user=followed_user)

        elif 'unfollow_user' in request.POST:  # Se désabonner d'un utilisateur
            follow_id = request.POST.get('unfollow_user')
            UserFollows.objects.filter(id=follow_id, user=request.user).delete()

        return redirect('follow-users-form')

    form = FollowUsersForm(user=request.user)
    followed_users = UserFollows.objects.filter(user=request.user)  # Utilisateurs suivis
    followers = UserFollows.objects.filter(followed_user=request.user)  # Abonnés

    return render(request, 'reviews/follow-users-form.html', {
        'form': form,
        'followed_users': followed_users,
        'followers': followers,
    })
