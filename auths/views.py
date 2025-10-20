from django.shortcuts import render, redirect
from .models import Auth
from django.contrib.auth import login,authenticate
from django.contrib import messages

def registro_view(request):
    if request.method == 'POST':
        pass
    return render(request, 'auths/registro.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('core:dashboard')  # o donde quieras redirigir
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'auths/login.html')
def logout_view(request):
    pass