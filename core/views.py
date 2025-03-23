from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Buchung, Konto, Vertrag, Kategorie
from .forms import (
    BuchungForm,
    BuchungEinnahmeForm,
    BuchungAusgabeForm,
    KontoForm,
    RegistrierungsForm,
    VertragForm,
    KategorieForm,
)

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
        return redirect('home')

    form = AuthenticationForm(data=request.POST or None)
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            form.add_error(None, "Benutzername oder Passwort ist falsch.")
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def buchung_list(request):
    buchungen = Buchung.objects.filter(konto__benutzer=request.user).select_related('konto', 'vertrag', 'kategorie')
    konten = Konto.objects.filter(benutzer=request.user)
    kategorien = Kategorie.objects.filter(benutzer=request.user)

    # --- Filter & Suche aus GET-Parametern ---
    selected_konto = request.GET.get('konto')
    selected_kategorie = request.GET.get('kategorie')
    search_query = request.GET.get('search')

    if selected_konto:
        buchungen = buchungen.filter(konto__kontonummer=selected_konto)
    if selected_kategorie:
        buchungen = buchungen.filter(kategorie__kategorienummer=selected_kategorie)
    if search_query:
        buchungen = buchungen.filter(beschreibung__icontains=search_query)

    # --- POST: Neue Buchung wird direkt auf dieser Seite erstellt ---
    if request.method == 'POST':
        # Unterscheide Einnahme/Ausgabe am hidden Feld oder QueryParam
        formtype = request.POST.get('formtype')
        if formtype == 'einnahme':
            form_einnahme = BuchungEinnahmeForm(request.POST, user=request.user)
            form_ausgabe = BuchungAusgabeForm(user=request.user)  # leer
            if form_einnahme.is_valid():
                form_einnahme.save()
                return redirect('buchung_list')
        elif formtype == 'ausgabe':
            form_ausgabe = BuchungAusgabeForm(request.POST, user=request.user)
            form_einnahme = BuchungEinnahmeForm(user=request.user)  # leer
            if form_ausgabe.is_valid():
                form_ausgabe.save()
                return redirect('buchung_list')
        else:
            # Fallback: evtl. altes BuchungForm
            form_einnahme = BuchungEinnahmeForm(user=request.user)
            form_ausgabe = BuchungAusgabeForm(user=request.user)
    else:
        form_einnahme = BuchungEinnahmeForm(user=request.user)
        form_ausgabe = BuchungAusgabeForm(user=request.user)

    context = {
        'buchungen': buchungen,
        'konten': konten,
        'kategorien': kategorien,
        'form_einnahme': form_einnahme,
        'form_ausgabe': form_ausgabe,
        'selected_konto': selected_konto,
        'selected_kategorie': selected_kategorie,
        'search_query': search_query,
    }
    return render(request, 'core/buchung_list.html', context)

@login_required
def buchung_create(request):
    # Falls du die alte Route "/buchungen/neu/" weiter nutzen möchtest
    if request.method == 'POST':
        form = BuchungForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('buchung_list')
    else:
        form = BuchungForm(user=request.user)
    return render(request, 'core/buchung_form.html', {'form': form})

@login_required
def buchung_update(request, pk):
    buchung = get_object_or_404(Buchung, pk=pk)
    if request.method == 'POST':
        form = BuchungForm(request.POST, instance=buchung, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('buchung_list')
    else:
        form = BuchungForm(instance=buchung, user=request.user)
    return render(request, 'core/buchung_form.html', {'form': form})

@login_required
def buchung_delete(request, pk):
    buchung = get_object_or_404(Buchung, pk=pk)
    if request.method == 'POST':
        buchung.delete()
        return redirect('buchung_list')
    return render(request, 'core/buchung_confirm_delete.html', {'buchung': buchung})

@login_required
def vertrag_list(request):
    vertraege = Vertrag.objects.filter(benutzer=request.user)
    return render(request, 'core/vertrag_list.html', {'vertraege': vertraege})

@login_required
def vertrag_create(request):
    if request.method == 'POST':
        form = VertragForm(request.POST, user=request.user)
        if form.is_valid():
            vertrag = form.save(commit=False)
            vertrag.benutzer = request.user
            vertrag.save()
            return redirect('vertrag_list')
    else:
        form = VertragForm(user=request.user)
    return render(request, 'core/vertrag_form.html', {'form': form})

@login_required
def vertrag_update(request, pk):
    vertrag = get_object_or_404(Vertrag, pk=pk, benutzer=request.user)
    if request.method == 'POST':
        form = VertragForm(request.POST, instance=vertrag, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('vertrag_list')
    else:
        form = VertragForm(instance=vertrag, user=request.user)
    return render(request, 'core/vertrag_form.html', {'form': form})

@login_required
def vertrag_delete(request, pk):
    vertrag = get_object_or_404(Vertrag, pk=pk, benutzer=request.user)
    if request.method == 'POST':
        vertrag.delete()
        return redirect('vertrag_list')
    return render(request, 'core/vertrag_confirm_delete.html', {'vertrag': vertrag})

@login_required
def konto_list(request):
    konten = Konto.objects.filter(benutzer=request.user)
    for konto in konten:
        konto.kontostand = konto.berechne_kontostand()
    return render(request, 'core/konto_list.html', {'konten': konten})

@login_required
def konto_create(request):
    if request.method == "POST":
        form = KontoForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('konto_list')
    else:
        form = KontoForm(user=request.user)
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

@login_required
def kategorie_list(request):
    kategorien = Kategorie.objects.filter(benutzer=request.user)
    return render(request, 'core/kategorie_list.html', {'kategorien': kategorien})

@login_required
def kategorie_create(request):
    if request.method == 'POST':
        form = KategorieForm(request.POST, user=request.user)
        if form.is_valid():
            kategorie = form.save(commit=False)
            kategorie.benutzer = request.user
            kategorie.save()
            return redirect('kategorie_list')
    else:
        form = KategorieForm(user=request.user)
    return render(request, 'core/kategorie_form.html', {'form': form})

@login_required
def kategorie_update(request, pk):
    kategorie = get_object_or_404(Kategorie, pk=pk, benutzer=request.user)
    if request.method == 'POST':
        form = KategorieForm(request.POST, instance=kategorie, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('kategorie_list')
    else:
        form = KategorieForm(instance=kategorie, user=request.user)
    return render(request, 'core/kategorie_form.html', {'form': form})

@login_required
def kategorie_delete(request, pk):
    kategorie = get_object_or_404(Kategorie, pk=pk, benutzer=request.user)
    if request.method == 'POST':
        kategorie.delete()
        return redirect('kategorie_list')
    return render(request, 'core/kategorie_confirm_delete.html', {'kategorie': kategorie})
