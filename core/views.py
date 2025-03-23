from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import Buchung, Konto, Vertrag, Kategorie, Budget
from .forms import (
    BuchungForm,
    BuchungEinnahmeForm,
    BuchungAusgabeForm,
    KontoForm,
    RegistrierungsForm,
    VertragForm,
    KategorieForm,
    BudgetForm
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
    buchungen = Buchung.objects.filter(konto__benutzer=request.user).select_related('konto', 'vertrag', 'kategorie').order_by('-buchungsdatum')
    konten = Konto.objects.filter(benutzer=request.user)
    kategorien = Kategorie.objects.filter(benutzer=request.user)

    selected_konto = request.GET.get('konto')
    selected_kategorie = request.GET.get('kategorie')
    search_query = request.GET.get('search')

    if selected_konto:
        buchungen = buchungen.filter(konto__kontonummer=selected_konto)
    if selected_kategorie:
        buchungen = buchungen.filter(kategorie__kategorienummer=selected_kategorie)
    if search_query:
        buchungen = buchungen.filter(beschreibung__icontains=search_query)

    form_einnahme = BuchungEinnahmeForm(user=request.user)
    form_ausgabe = BuchungAusgabeForm(user=request.user)

    # Formulare für alle bestehenden Buchungen (zum Bearbeiten)
    formularliste_bearbeiten = [
        (buchung, BuchungForm(instance=buchung, user=request.user))
        for buchung in buchungen
    ]

    if request.method == 'POST':
        formtype = request.POST.get('formtype')
        if formtype == 'einnahme':
            form_einnahme = BuchungEinnahmeForm(request.POST, user=request.user)
            if form_einnahme.is_valid():
                form_einnahme.save()
                return redirect('buchung_list')
        elif formtype == 'ausgabe':
            form_ausgabe = BuchungAusgabeForm(request.POST, user=request.user)
            if form_ausgabe.is_valid():
                form_ausgabe.save()
                return redirect('buchung_list')
        elif formtype == 'bearbeiten':
            buchung_id = request.POST.get('buchung_id')
            buchung = get_object_or_404(Buchung, pk=buchung_id, konto__benutzer=request.user)
            form = BuchungForm(request.POST, instance=buchung, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('buchung_list')

    context = {
        'buchungen': buchungen,
        'konten': konten,
        'kategorien': kategorien,
        'form_einnahme': form_einnahme,
        'form_ausgabe': form_ausgabe,
        'formularliste_bearbeiten': formularliste_bearbeiten,
        'selected_konto': selected_konto,
        'selected_kategorie': selected_kategorie,
        'search_query': search_query,
    }
    return render(request, 'core/buchung_list.html', context)

@login_required
def buchung_create(request):
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
    buchung = get_object_or_404(Buchung, pk=pk, konto__benutzer=request.user)
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
    buchung = get_object_or_404(Buchung, pk=pk, konto__benutzer=request.user)
    if request.method == 'POST':
        buchung.delete()
    return redirect('buchung_list')

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

@login_required
def budget_list(request):
    from datetime import date

    monat = request.GET.get('monat')
    if monat:
        jahr, monat_num = map(int, monat.split('-'))
        aktueller_monat = date(jahr, monat_num, 1)
    else:
        aktueller_monat = date.today().replace(day=1)

    budgets = Budget.objects.filter(benutzer=request.user)
    form_create = BudgetForm(user=request.user)

    # Neue Datenstruktur: Liste mit Budget + Ausgaben & Restbetrag
    budgets_mit_auswertung = []
    for budget in budgets:
        verbraucht = budget.berechne_ausgaben(aktueller_monat)
        rest = budget.betrag - verbraucht
        prozent = (verbraucht if budget.betrag else 0) / budget.betrag * 100 if budget.betrag else 0
        budgets_mit_auswertung.append({
            'obj': budget,
            'rest': rest,
            'verbrauch': verbraucht,
            'prozent': round(prozent),
        })

    formulare_bearbeiten = {
        b.id: BudgetForm(instance=b, user=request.user) for b in budgets
    }

    return render(request, 'core/budget_list.html', {
        'budgets': budgets,
        'budgets_mit_auswertung': budgets_mit_auswertung,
        'form_create': form_create,
        'formulare_bearbeiten': formulare_bearbeiten,
        'aktueller_monat': aktueller_monat,
    })

@login_required
def budget_create(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)
    return redirect('budget_list')


@login_required
def budget_update(request, pk):
    budget = get_object_or_404(Budget, pk=pk, benutzer=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    return render(request, 'core/budget_form.html', {'form': form})

@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, benutzer=request.user)
    if request.method == 'POST':
        budget.delete()
        return redirect('budget_list')
    return render(request, 'core/budget_confirm_delete.html', {'budget': budget})