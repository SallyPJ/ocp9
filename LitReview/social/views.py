from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import UserFollows  # Modèle UserFollows
from .forms import FollowUsersForm

User = get_user_model()


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
            follow_relation = get_object_or_404(UserFollows, id=follow_id,
                                                followed_user=request.user)
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
