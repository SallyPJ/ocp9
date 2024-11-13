from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout



def logout_user(request):
    logout(request)
    return redirect('login')


