from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Buchung, Konto, Vertrag
from .forms import BuchungForm, KontoForm, RegistrierungsForm, VertragForm


@login_required
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
    if request.user.is_authenticated:
        return redirect('buchung_list')  # Falls bereits eingeloggt, weiterleiten

    form = AuthenticationForm(data=request.POST or None)
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('buchung_list')  # Erfolgreicher Login -> Weiterleitung
        else:
            form.add_error(None, "Benutzername oder Passwort ist falsch.")  # Allgemeine Fehlermeldung

    return render(request, 'core/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def buchung_list(request):
    # Hole nur die Buchungen des aktuell eingeloggten Benutzers
    buchungen = Buchung.objects.filter(konto__benutzer=request.user).select_related('konto', 'vertrag', 'kategorie').all()
    return render(request, 'core/buchung_list.html', {'buchungen': buchungen})


@login_required
def buchung_create(request):
    if request.method == 'POST':
        form = BuchungForm(request.POST, user=request.user)  # Übergabe des aktuellen Benutzers
        if form.is_valid():
            buchung = form.save(commit=False)
            buchung.save()
            return redirect('buchung_list')  # Weiterleitung zur Buchungsliste
    else:
        form = BuchungForm(user=request.user)  # Übergabe des aktuellen Benutzers

    return render(request, 'core/buchung_form.html', {'form': form})


@login_required
def buchung_update(request, pk):
    buchung = get_object_or_404(Buchung, pk=pk)
    if request.method == 'POST':
        form = BuchungForm(request.POST, instance=buchung, user=request.user)  # Übergabe des aktuellen Benutzers
        if form.is_valid():
            form.save()
            return redirect('buchung_list')
    else:
        form = BuchungForm(instance=buchung, user=request.user)  # Übergabe des aktuellen Benutzers

    return render(request, 'core/buchung_form.html', {'form': form})

@login_required
def vertrag_list(request):
    """ Zeigt alle Verträge des eingeloggten Benutzers an """
    vertraege = Vertrag.objects.filter(benutzer=request.user)
    return render(request, 'core/vertrag_list.html', {'vertraege': vertraege})


@login_required
def vertrag_create(request):
    """ Erstellt einen neuen Vertrag """
    if request.method == "POST":
        form = VertragForm(request.POST)
        if form.is_valid():
            vertrag = form.save(commit=False)
            vertrag.benutzer = request.user  # Automatische Benutzerzuweisung
            vertrag.save()
            return redirect('vertrag_list')  # Weiterleitung zur Vertragsliste
    else:
        form = VertragForm()

    return render(request, 'core/vertrag_form.html', {'form': form})


@login_required
def vertrag_update(request, pk):
    """ Bearbeitet einen bestehenden Vertrag """
    vertrag = get_object_or_404(Vertrag, pk=pk, benutzer=request.user)
    if request.method == "POST":
        form = VertragForm(request.POST, instance=vertrag)
        if form.is_valid():
            form.save()
            return redirect('vertrag_list')
    else:
        form = VertragForm(instance=vertrag)

    return render(request, 'core/vertrag_form.html', {'form': form})


@login_required
def vertrag_delete(request, pk):
    """ Löscht einen Vertrag """
    vertrag = get_object_or_404(Vertrag, pk=pk, benutzer=request.user)
    if request.method == "POST":
        vertrag.delete()
        return redirect('vertrag_list')

    return render(request, 'core/vertrag_confirm_delete.html', {'vertrag': vertrag})


@login_required
def vertrag_erneuern(request):
    """ Erstellt automatisch Buchungen basierend auf bestehenden Verträgen """
    vertraege = Vertrag.objects.filter(benutzer=request.user)

    for vertrag in vertraege:
        if vertrag.ablaufdatum <= timezone.now().date():
            vertrag.delete()  # Vertrag löschen, wenn Ablaufdatum erreicht ist
        else:
            # Neue Buchung für den Vertrag generieren
            Buchung.objects.create(
                betrag=vertrag.betrag,
                buchungsdatum=timezone.now().date(),
                buchungsart="Ausgabe",
                konto=vertrag.konto,
                kategorie=vertrag.kategorie,
                vertrag=vertrag
            )

    return redirect('vertrag_list')

@login_required
def buchung_delete(request, pk):
    buchung = get_object_or_404(Buchung, pk=pk)
    if request.method == 'POST':
        buchung.delete()
        return redirect('buchung_list')
    return render(request, 'core/buchung_confirm_delete.html', {'buchung': buchung})

@login_required
def konto_list(request):
    # Hole nur die Konten des aktuell eingeloggten Benutzers
    konten = Konto.objects.filter(benutzer=request.user)
    for konto in konten:
        konto.kontostand = konto.berechne_kontostand()  # Berechne den Kontostand für jedes Konto
    return render(request, 'core/konto_list.html', {'konten': konten})

@login_required
def konto_create(request):
    if request.method == "POST":
        form = KontoForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('konto_list')  # Passe den Namen der Zielseite an
    else:
        form = KontoForm(user=request.user)  # Hier wird das Formular für GET-Requests initialisiert

    return render(request, 'core/konto_form.html', {'form': form})

@login_required
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

@login_required
def konto_delete(request, pk):
    konto = get_object_or_404(Konto, pk=pk)
    if request.method == 'POST':
        konto.delete()
        return redirect('konto_list')
    return render(request, 'core/konto_confirm_delete.html', {'konto': konto})