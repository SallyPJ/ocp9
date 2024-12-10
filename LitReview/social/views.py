from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserFollows  # Modèle UserFollows
from .forms import FollowUsersForm

User = get_user_model()


@login_required
def follow_users_form(request):
    if request.method == 'POST':
        if 'follow_user' in request.POST:  # Suivre un utilisateur
            form = FollowUsersForm(request.POST, user=request.user)

            if form.is_valid():
                followed_user = form.cleaned_data['followed_username']
                try:
                    followed_user = User.objects.get(username=followed_user)
                    if followed_user != request.user:  # Empêche de se suivre soi-même
                        follow, created = UserFollows.objects.get_or_create(
                            user=request.user,
                            followed_user=followed_user
                        )
                        if created:
                            messages.success(request, f"Vous suivez maintenant {followed_user.username}.")
                        else:
                            messages.warning(request, f"Vous suivez déjà {followed_user.username}.")
                    else:
                        messages.error(request, "Vous ne pouvez pas vous suivre vous-même.")
                except User.DoesNotExist:
                    messages.error(request, f"L'utilisateur '{followed_user}' n'existe pas.")
            else:
                messages.error(request, "Formulaire non valide. Veuillez vérifier votre saisie.")

        elif 'unfollow_user' in request.POST:  # Se désabonner d'un utilisateur
            follow_id = request.POST.get('unfollow_user')
            UserFollows.objects.filter(id=follow_id, user=request.user).delete()

        elif 'block_user' in request.POST:  # Bloquer/Débloquer un utilisateur
            follow_id = request.POST.get('block_user')
            follow_relation = get_object_or_404(UserFollows, id=follow_id,
                                                followed_user=request.user)
            follow_relation.blocked = not follow_relation.blocked  # Inverse l'état de blocage
            follow_relation.save()

        return redirect('follow-users-form')

    form = FollowUsersForm(user=request.user)
    followed_users = UserFollows.objects.filter(user=request.user)  # Utilisateurs suivis
    followers = UserFollows.objects.filter(followed_user=request.user)  # Abonnés

    return render(request, 'social/follow-users-form.html', {
        'form': form,
        'followed_users': followed_users,
        'followers': followers,
    })
