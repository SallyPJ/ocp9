from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Ticket, Review
from .forms import ReviewForm, TicketForm, PhotoForm
from social.models import UserFollows
from django.core.paginator import Paginator
from . import forms
from itertools import chain


@login_required
def home(request):
    """
    View for displaying the home feed.

    Retrieves tickets and reviews from followed users and the current user,
    excluding content from blocked users.
    """
    # Retrieve users blocked by the current user
    blocked_users = (UserFollows.objects.filter(user=request.user, blocked=True)
                     .values_list('followed_user', flat=True))

    # Retrieve users who blocked the current user
    blocked_by_users = (UserFollows.objects.filter(followed_user=request.user, blocked=True)
                        .values_list('user', flat=True))

    # Combine all blocked users into a single set
    blocked_combined = set(blocked_users).union(set(blocked_by_users))

    # Retrieve IDs of followed users
    followed_users = request.user.following.values_list('followed_user', flat=True)

    # Fetch tickets from followed users and the current user, excluding blocked users
    tickets = Ticket.objects.filter(
        (Q(user__in=followed_users) | Q(user=request.user))
        & ~Q(user__in=blocked_combined)  # Exclure les utilisateurs bloqués
    ).prefetch_related('review_set')

    # Annotate tickets with a flag to indicate if the user has reviewed them
    # (to deactivate review button)
    for ticket in tickets:
        ticket.user_has_reviewed = (ticket.review_set.filter
                                    (user=request.user).exists())

    # Fetch reviews from followed users, the current user,
    # or tickets created by the user
    reviews = Review.objects.filter(
        (Q(user__in=followed_users) |  # Reviews by followed users
         Q(user=request.user) |  # Reviews by the user
         Q(ticket__user=request.user))  # Reviews on tickets created by the user
        & ~Q(user__in=blocked_combined)  # Exclude blocked users
    ).select_related('ticket')

    # Combine and sort tickets and reviews by creation time
    posts = sorted(chain(tickets, reviews),
                   key=lambda instance: instance.time_created,
                   reverse=True)
    print("Tickets :", list(tickets))
    print("Reviews :", list(reviews))
    print("Posts combinés :", posts)

    # Paginate the posts (6 per page)
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    # Render the home page with paginated posts
    context = {
        'page_obj': page_obj,
        }
    return render(request, 'reviews/home.html', context=context)


@login_required
def create_or_edit_ticket(request, ticket_id=None):
    """
    View for creating or editing a ticket.

    Args:
        ticket_id (int): ID of the ticket to edit (if any).

    Returns:
        HttpResponse: Renders the ticket creation or edit page.
    """
    # Fetch the ticket if an ID is provided; otherwise, create a new ticket
    if ticket_id:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        if ticket.user != request.user:
            return HttpResponseForbidden("Vous n'êtes pas autorisé"
                                         " à modifier ce billet.")
    else:
        ticket = Ticket(user=request.user)

    # Initialize forms for ticket and photo
    ticket_form = TicketForm(instance=ticket)
    photo_form = PhotoForm(instance=ticket.photo)

    if request.method == 'POST':
        # Bind form data
        ticket_form = TicketForm(request.POST, instance=ticket)
        photo_form = PhotoForm(request.POST, request.FILES, instance=ticket.photo)

        # Validate both forms
        if ticket_form.is_valid() and photo_form.is_valid():
            ticket = ticket_form.save(commit=False)

            # Handle the optional photo upload
            if photo_form.cleaned_data.get('image'):
                photo = photo_form.save(commit=False)
                photo.uploader = request.user
                photo.save()
                ticket.photo = photo

            ticket.save()
            # Redirect to appropriate page after saving
            if ticket_id:  # Ticket modification
                return redirect('posts')
            else:  # Ticket creation
                return redirect('home')

    # Render the ticket management page with forms
    context = {
        'ticket_form': ticket_form,
        'photo_form': photo_form,
        'is_edit': ticket_id is not None,
    }
    return render(request, 'reviews/manage-ticket.html', context)


@login_required()
def delete_ticket(request, ticket_id):
    """
    View for deleting a ticket.

    Args:
        ticket_id (int): ID of the ticket to delete.

    Returns:
        HttpResponse: Renders the confirmation page or redirects after deletion.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.user != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé "
                                     "à supprimer ce billet.")

    if request.method == 'POST':
        ticket.delete()
        return redirect('posts')  # Redirect after deletion

    return render(request, 'reviews/confirm-delete.html',
                  {'ticket': ticket})


@login_required
def create_or_edit_review(request, ticket_id=None, review_id=None):
    """
    View for creating or editing a review.

    Args:
        ticket_id (int): ID of the ticket associated with the review.
        review_id (int): ID of the review to edit (if any).

    Returns:
        HttpResponse: Renders the review creation or edit page.
    """
    # Fetch the ticket if ticket_id is provided
    if ticket_id:
        ticket = get_object_or_404(Ticket, id=ticket_id)
    else:
        ticket = None

    # Fetch the review if review_id is provided; otherwise, create a new review
    if review_id:
        review = get_object_or_404(Review, id=review_id)
        if review.user != request.user:
            return HttpResponseForbidden("Vous n'êtes pas autorisé"
                                         " à modifier cette critique.")
        ticket = review.ticket
    else:
        review = Review(ticket=ticket, user=request.user)

    # Initialize the review form
    review_form = ReviewForm(instance=review)

    is_edit = review_id is not None
    is_reply_mode = True

    if request.method == 'POST':
        # Bind form data
        review_form = ReviewForm(request.POST, instance=review)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            if not review_id:
                review.ticket = ticket  # Associate to ticket when review is created
            review.save()
            if review_id:  # Modification
                return redirect('posts')
            else:  # Creation
                return redirect('home')

    # Render the review management page with the form
    context = {
        'review_form': review_form,
        'ticket': ticket,
        'is_reply_mode': is_reply_mode,
        'is_edit': is_edit,
    }
    return render(request, 'reviews/manage-review.html', context)


@login_required()
def delete_review(request, review_id):
    """
    View for deleting a review.

    Args:
        review_id (int): ID of the review to delete.

    Returns:
        HttpResponse: Renders the confirmation page or redirects after deletion.
    """
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
    """
    View to create both a ticket and a linked review in a single form submission.

    This view allows the user to create a ticket and immediately link a review to it.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Renders the 'create-ticket-and-review.html' template
        or redirects to the home page if the form is successfully submitted.

    Workflow:
        - On GET request, empty forms for Ticket, Photo, and Review are displayed.
        - On POST request, form data is validated:
            1. If valid, a new Ticket, Photo (if uploaded), and Review are saved.
            2. If invalid, the form is re-rendered with error messages.
    """
    # Initialize empty forms for Ticket, Photo, and Review (GET request)
    ticket_form = forms.TicketForm()
    photo_form = forms.PhotoForm()
    review_form = forms.ReviewForm()

    if request.method == 'POST':
        # Bind form data to the forms (POST request)
        ticket_form = forms.TicketForm(request.POST)
        photo_form = forms.PhotoForm(request.POST, request.FILES)
        review_form = forms.ReviewForm(request.POST)
        # Check if all forms are valid
        if all([ticket_form.is_valid(), photo_form.is_valid(), review_form.is_valid()]):
            # Save the photo (if uploaded) but don't commit to the database yet
            photo = photo_form.save(commit=False)
            photo.uploader = request.user
            photo.save()
            # Save the ticket (assigning the user) but don't commit to the database yet
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            # Check if an image is uploaded and attach it to the ticket
            if photo_form.cleaned_data.get('image'):
                photo = photo_form.save(commit=False)
                photo.uploader = request.user
                photo.save()
                ticket.photo = photo
            else:
                ticket.photo = None
            # Save the ticket in the database
            ticket.save()

            # Save the review (linking it to the ticket) but don't commit to the database yet
            review = review_form.save(commit=False)
            # Attach the logged-in user
            review.user = request.user
            # Link the review to the ticket
            review.ticket = ticket
            review.save()
            return redirect('home')
        else:
            # Afficher les erreurs de validation pour débogage
            print("Erreurs dans ticket_form :", ticket_form.errors)
            print("Erreurs dans photo_form :", photo_form.errors)
    # Render the page with empty or pre-filled forms
    context = {
        'ticket_form': ticket_form,
        'photo_form': photo_form,
        'review_form': review_form,
    }
    return render(request, 'reviews/create-ticket-and-review.html', context=context)


@login_required()
def display_user_posts(request):
    """
       View to display the current user's posts (both tickets and reviews).

       This view retrieves all the tickets and reviews created by the current user,
       merges them, and sorts them by creation date (newest first). The posts
       are paginated to display 6 posts per page.

       Args:
           request (HttpRequest): The incoming HTTP request.

       Returns:
           HttpResponse: Renders the 'posts.html' template with a paginated list of the user's posts.

       Workflow:
           - Retrieve all tickets created by the user.
           - Retrieve all reviews created by the user.
           - Merge the two querysets and sort by `time_created` in descending order.
           - Paginate the results (6 posts per page).
           - Render the posts.html page with the list of posts.
       """
    # Retrieve all tickets created by the user, along with their associated reviews
    user_tickets = Ticket.objects.filter(user=request.user).prefetch_related('review_set')

    # Retrieve all reviews created by the user, along with the associated ticket
    user_reviews = Review.objects.filter(user=request.user).select_related('ticket')

    # Merge and sort tickets and reviews by time_created (newest first)
    posts = sorted(
        chain(user_tickets, user_reviews),
        key=lambda instance: instance.time_created,
        reverse=True
    )

    # Paginate the posts (6 posts per page)
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    # Render the 'posts.html' page with the paginated list of posts
    context = {
        'page_obj': page_obj,
        'show_buttons': True,
    }
    return render(request, 'reviews/posts.html',
                  context=context)
