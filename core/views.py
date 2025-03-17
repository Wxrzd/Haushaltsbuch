from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Buchung, Konto, Vertrag
from .forms import BuchungForm, KontoForm, RegistrierungsForm, LoginForm

def home(request):
    return render(request, 'core/home.html')

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
    buchungen = Buchung.objects.select_related('KontoNr', 'VertragsNr', 'KategorieNr').all()
    return render(request, 'core/buchung_list.html', {'buchungen': buchungen})

def buchung_create(request):
    if request.method == 'POST':
        form = BuchungForm(request.POST)
        if form.is_valid():
            buchung = form.save(commit=False)
            buchung.save()
            return redirect('buchung_list')  # Zur Buchungsliste weiterleiten
    else:
        form = BuchungForm()

    return render(request, 'core/buchung_form.html', {'form': form})

def buchung_update(request, pk):
    buchung = get_object_or_404(Buchung, pk=pk)
    if request.method == 'POST':
        form = BuchungForm(request.POST, instance=buchung)
        if form.is_valid():
            form.save()
            return redirect('buchung_list')
    else:
        form = BuchungForm()
    return render(request, 'core/buchung_form.html', {'form': form})

class VertragsListeView(ListView):
    model = Vertrag
    template_name = 'vertraege/vertrags_liste.html'  # Pfad zur HTML-Vorlage
    context_object_name = 'vertraege'  # Name der Variable im Template
        form = BuchungForm(instance=buchung)
    return render(request, 'core/buchung_form.html', {'form': form})

def buchung_delete(request, pk):
    buchung = get_object_or_404(Buchung, pk=pk)
    if request.method == 'POST':
        buchung.delete()
        return redirect('buchung_list')
    return render(request, 'core/buchung_confirm_delete.html', {'buchung': buchung})

def konto_list(request):
    konten = Konto.objects.all()
    for konto in konten:
        konto.Kontostand = konto.berechne_kontostand()  # Aktualisiere den Kontostand
    return render(request, 'core/konto_list.html', {'konten': konten})

def konto_create(request):
    if request.method == 'POST':
        form = KontoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('konto_list')
    else:
        form = KontoForm()
    return render(request, 'core/konto_form.html', {'form': form})

def konto_update(request, pk):
    konto = get_object_or_404(Konto, pk=pk)
    if request.method == 'POST':
        form = KontoForm(request.POST, instance=konto)
        if form.is_valid():
            form.save()
            return redirect('konto_list')
    else:
        form = KontoForm(instance=konto)
    return render(request, 'core/konto_form.html', {'form': form})

def konto_delete(request, pk):
    konto = get_object_or_404(Konto, pk=pk)
    if request.method == 'POST':
        konto.delete()
        return redirect('konto_list')
    return render(request, 'core/konto_confirm_delete.html', {'konto': konto})
