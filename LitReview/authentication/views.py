from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.conf import settings

from . import forms


def logout_user(request):
    """
    Logs out the current user and redirects to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects the user to the login page.
    """
    logout(request)
    return redirect('login')


def signup_user(request):
    """
    Handles user signup by displaying a signup form and processing user registration.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the signup page with a form context or redirects after successful signup.

    Workflow:
        - If the request method is GET, an empty signup form is displayed.
        - If the request method is POST:
            1. Validate the submitted form data.
            2. If valid, create a new user and log them in automatically.
            3. Redirect the user to the LOGIN_REDIRECT_URL.
        - If the form is invalid, re-render the signup page with the form errors.
    """
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authentication/signup_page.html', context={'form': form})
