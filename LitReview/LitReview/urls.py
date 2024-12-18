"""
URL configuration for LitReview project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('reviews/', include('reviews.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import (
    LoginView, LogoutView)
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from authentication.forms import CustomAuthenticationForm
import authentication.views
import reviews.views
import social.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(
        template_name='authentication/authentication_page.html',
        redirect_authenticated_user=True,
        authentication_form=CustomAuthenticationForm  # Utilisation du formulaire personnalisé
    ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', authentication.views.signup_user, name='signup'),
    path('home/', reviews.views.home, name='home'),
    path('reviews/create-ticket/', reviews.views.create_or_edit_ticket, name='create-ticket'),
    path('reviews/<int:ticket_id>/edit', reviews.views.create_or_edit_ticket, name='edit-ticket'),
    path('reviews/<int:review_id>/edit/', reviews.views.create_or_edit_review, name='edit-review'),
    path('reviews/<int:review_id>/delete/', reviews.views.delete_review, name='delete-review'),
    path('delete-ticket/<int:ticket_id>/', reviews.views.delete_ticket, name='delete-ticket'),
    path('create-review/<int:ticket_id>/', reviews.views.create_or_edit_review,
         name='create-review'),
    path('create_both_ticket_review/', reviews.views.create_ticket_and_review,
         name='create-ticket-and-review'),
    path('reviews/my-posts.html/', reviews.views.display_user_posts, name='posts'),
    path('follow-users-form/', social.views.follow_users_form, name='follow-users-form'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
