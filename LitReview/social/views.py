from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserFollows
from .forms import FollowUsersForm

User = get_user_model()


@login_required
def follow_users_form(request):
    """
        View to manage user follow, unfollow, and block actions.

        This view allows the authenticated user to:
        - Follow another user by submitting their username.
        - Unfollow an existing followed user.
        - Block or unblock a user.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            HttpResponse: Renders the 'follow_user_page.html' template
                          or redirects after processing POST requests.

        Workflow:
            - **GET request**:
                - Renders the page with the follow form and lists the users being followed
                  and the followers of the current user.
            - **POST request**:
                - Handles three actions based on POST data:
                    1. **Follow User**: Creates a follow relationship with another user.
                    2. **Unfollow User**: Removes an existing follow relationship.
                    3. **Block/Unblock User**: Toggles the block status of an
                    existing follow relationship.
        """
    if request.method == 'POST':
        if 'follow_user' in request.POST:
            form = FollowUsersForm(request.POST, user=request.user)

            if form.is_valid():
                followed_username = form.cleaned_data['followed_username']

                # Get the user to be followed based on the username from the form
                followed_user = User.objects.get(username=followed_username)

                # Create the follow relationship if it does not already exist
                follow, created = UserFollows.objects.get_or_create(
                    user=request.user,
                    followed_user=followed_user
                )

                if created:
                    messages.success(request, f"Vous suivez maintenant {followed_username}.")
                else:
                    messages.warning(request, f"Vous suivez déjà {followed_username}.")
            else:
                # Display error messages if the form is invalid
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Erreur : {error}")

        elif 'unfollow_user' in request.POST:  # Handle unfollow action
            follow_id = request.POST.get('unfollow_user')
            UserFollows.objects.filter(id=follow_id, user=request.user).delete()

        elif 'block_user' in request.POST:  # Handle block/unblock action
            follow_id = request.POST.get('block_user')
            follow_relation = get_object_or_404(UserFollows, id=follow_id,
                                                followed_user=request.user)
            follow_relation.blocked = not follow_relation.blocked  # Inverse l'état de blocage
            follow_relation.save()

        return redirect('follow-users-form')

    # Form for entering the username to follow
    form = FollowUsersForm(user=request.user)
    followed_users = UserFollows.objects.filter(user=request.user)  # Utilisateurs suivis
    followers = UserFollows.objects.filter(followed_user=request.user)  # Abonnés

    return render(request, 'social/follow_users_page.html', {
        'form': form,
        'followed_users': followed_users,
        'followers': followers,
    })
