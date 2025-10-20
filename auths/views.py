from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Auth
from django.contrib.auth import login

def registro_view(request):
    if request.method == 'POST':
        pass
    return render(request, 'auths/registro.html')

def login_view(request):
    if request.method == 'POST':
        pass
    return render(request, 'auths/login.html')