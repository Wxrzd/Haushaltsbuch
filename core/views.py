from django.shortcuts import render, redirect
from .models import Buchung
from .forms import BuchungForm

def home(request):
    return render(request, 'core/home.html')

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import RegistrierungsForm, LoginForm

def registrierung_view(request):
    if request.method == 'POST':
        form = RegistrierungsForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrierungsForm()
    return render(request, 'core/registrierung.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Ungültiger Benutzername oder falsches Passwort.")
    
    form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

def buchung_list(request):
    buchungen = Buchung.objects.all()
    return render(request, 'core/buchung_list.html', {'buchungen': buchungen})

def buchung_create(request):
    if request.method == 'POST':
        form = BuchungForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('buchung_list')
    else:
        form = BuchungForm()
    return render(request, 'core/buchung_form.html', {'form': form})