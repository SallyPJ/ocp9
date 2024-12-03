from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Ticket, Photo, Review, UserFollows
from .forms import FollowUsersForm, ReviewForm, TicketForm, PhotoForm
from django.core.paginator import Paginator
from . import forms
from itertools import chain



@login_required
def home(request):
    # Liste des utilisateurs bloqués par l'utilisateur connecté
    blocked_users = UserFollows.objects.filter(user=request.user, blocked=True).values_list('followed_user', flat=True)

    # Liste des utilisateurs ayant bloqué l'utilisateur connecté
    blocked_by_users = UserFollows.objects.filter(followed_user=request.user, blocked=True).values_list('user',
                                                                                                        flat=True)

    # Liste combinée des utilisateurs bloqués dans les deux sens
    blocked_combined = set(blocked_users).union(set(blocked_by_users))

    followed_users = request.user.following.values_list('followed_user', flat=True)

    # Liste des utilisateurs qui sont suivis par l'utilisateur connecté
    # Récupère tous les tickets avec leurs critiques associées
    tickets = Ticket.objects.filter(
        (Q(user__in=followed_users) | Q(user=request.user))
        & ~Q(user__in=blocked_combined)  # Exclure les utilisateurs bloqués
    ).prefetch_related('review_set')

    # Ajouter une annotation pour vérifier si l'utilisateur a écrit une critique sur chaque ticket
    for ticket in tickets:
        ticket.user_has_reviewed = ticket.review_set.filter(user=request.user).exists()

    # Récupère toutes les critiques avec leur ticket lié
    reviews = Review.objects.filter(
        (Q(user__in=followed_users) |  # Reviews des utilisateurs suivis
         Q(user=request.user) |  # Reviews de l'utilisateur connecté
         Q(ticket__user=request.user))  # Reviews des tickets créés par l'utilisateur connecté
        & ~Q(user__in=blocked_combined)  # Exclure les utilisateurs bloqués
    ).select_related('ticket')

    posts = sorted(chain(tickets, reviews),
                   key=lambda instance: instance.time_created,
                   reverse=True)
    print("Tickets :", list(tickets))
    print("Reviews :", list(reviews))
    print("Posts combinés :", posts)

    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'page_obj': page_obj,
        }
    # Transmet les données au template
    return render(request, 'reviews/home.html', context=context)


@login_required
def create_or_edit_ticket(request, ticket_id=None):
    # Si `ticket_id` est fourni, on édite un ticket existant, sinon on crée un nouveau ticket
    if ticket_id:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if ticket.user != request.user:
            return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier ce billet.")
    else:
        ticket = Ticket(user=request.user)

    # Initialisez les formulaires
    ticket_form = TicketForm(instance=ticket)
    photo_form = PhotoForm(instance=ticket.photo)

    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, instance=ticket)
        photo_form = PhotoForm(request.POST, request.FILES, instance=ticket.photo)

        if ticket_form.is_valid() and photo_form.is_valid():
            # Sauvegarder le ticket
            ticket = ticket_form.save(commit=False)

            # Sauvegarder ou mettre à jour l'image
            if photo_form.cleaned_data.get('image'):
                photo = photo_form.save(commit=False)
                photo.uploader = request.user
                photo.save()
                ticket.photo = photo

            ticket.save()
            if ticket_id:  # Modification
                return redirect('posts')
            else:  # Création
                return redirect('home')

    context = {
        'ticket_form': ticket_form,
        'photo_form': photo_form,
        'is_edit': ticket_id is not None,  # Indique si c'est une édition
    }
    return render(request, 'reviews/manage-ticket.html', context)



@login_required()
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Vérifie que l'utilisateur est le propriétaire du ticket
    if ticket.user != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à supprimer ce billet.")

    if request.method == 'POST':
        ticket.delete()
        return redirect('posts')  # Redirige après la suppression

    return render(request, 'reviews/confirm-delete.html', {'ticket': ticket})


@login_required
def create_or_edit_review(request, ticket_id=None, review_id=None):
    # Récupère le ticket si ticket_id est fourni
    if ticket_id:
        ticket = get_object_or_404(Ticket, id=ticket_id)
    else:
        ticket = None

    # Récupère ou initialise une review
    if review_id:
        review = get_object_or_404(Review, id=review_id)
        if review.user != request.user:
            return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier cette critique.")
        ticket = review.ticket
    else:
        review = Review(ticket=ticket, user=request.user)

    # Pré-remplit le formulaire
    review_form = ReviewForm(instance=review)

    is_edit = review_id is not None
    is_reply_mode = True

    if request.method == 'POST':
        review_form = ReviewForm(request.POST, instance=review)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            if not review_id:
                review.ticket = ticket  # Associe le ticket lors de la création
            review.save()
            if review_id:  # Modification
                return redirect('posts')
            else:  # Création
                return redirect('home')

    context = {
        'review_form': review_form,
        'ticket': ticket,
        'is_reply_mode': is_reply_mode,
        'is_edit': is_edit,
    }
    return render(request, 'reviews/manage-review.html', context)


@login_required()
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à supprimer cette critique.")

    if request.method == 'POST':
        review.delete()
        return redirect('posts')

    context = {'review': review}
    return render(request, 'reviews/confirm-delete-review.html', context)

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
            # Gestion de l'image optionnelle
            if photo_form.cleaned_data.get('image'):  # Vérifie si une image a été téléchargée
                photo = photo_form.save(commit=False)
                photo.uploader = request.user
                photo.save()
                ticket.photo = photo
            else:
                ticket.photo = None
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
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'page_obj': page_obj,
        'show_buttons': True,
    }

    return render(request, 'reviews/posts.html',
                  context=context)

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

        elif 'block_user' in request.POST:  # Bloquer/Débloquer un utilisateur
            follow_id = request.POST.get('block_user')
            follow_relation = get_object_or_404(UserFollows, id=follow_id, followed_user=request.user)
            follow_relation.blocked = not follow_relation.blocked  # Inverse l'état de blocage
            follow_relation.save()

        return redirect('follow-users-form')

    form = FollowUsersForm(user=request.user)
    followed_users = UserFollows.objects.filter(user=request.user)  # Utilisateurs suivis
    followers = UserFollows.objects.filter(followed_user=request.user)  # Abonnés

    return render(request, 'reviews/follow-users-form.html', {
        'form': form,
        'followed_users': followed_users,
        'followers': followers,
    })


