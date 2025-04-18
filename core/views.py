from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.urls import reverse
from datetime import date
import calendar
from .forms import get_kategorie_choices
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



# Home Views
@login_required
def home(request):
    aktueller_monat = date.today().replace(day=1)
    budgets = Budget.objects.filter(benutzer=request.user)

    budgets_mit_auswertung = []
    for budget in budgets:
        verbraucht = budget.berechne_ausgaben(aktueller_monat)
        rest = budget.betrag - verbraucht
        prozent = 0
        if budget.betrag > 0:
            prozent = (verbraucht / budget.betrag) * 100

        budgets_mit_auswertung.append({
            'obj': budget,
            'rest': rest,
            'verbrauch': verbraucht,
            'prozent': round(prozent),
        })

    konten = Konto.objects.filter(benutzer=request.user)
    sum_kontostaende = 0
    for k in konten:
        k.kontostand = k.berechne_kontostand()
        sum_kontostaende += k.kontostand
    alle_vertraege = list(Vertrag.objects.filter(benutzer=request.user))
    alle_vertraege = [v for v in alle_vertraege if v.naechste_buchung is not None]
    alle_vertraege.sort(key=lambda x: x.naechste_buchung)
    vertraege_ausstehend = alle_vertraege[:4]
    letzte_buchungen = Buchung.objects.filter(
        konto__benutzer=request.user
    ).select_related('konto', 'vertrag', 'kategorie').order_by('-buchungsdatum')[:8]

    context = {
        'budgets_mit_auswertung': budgets_mit_auswertung,
        'aktueller_monat': aktueller_monat,
        'konten': konten,
        'sum_kontostaende': sum_kontostaende,
        'vertraege_ausstehend': vertraege_ausstehend,
        'letzte_buchungen': letzte_buchungen,
    }
    return render(request, 'core/home.html', context)



# Authentication Views
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



# Buchung Views
@login_required
def buchung_list(request):
    konten = Konto.objects.filter(benutzer=request.user)
    grouped_kategorien = get_kategorie_choices(request.user)

    selected_monat = request.GET.get('monat')
    if not selected_monat:
        selected_monat = date.today().strftime('%Y-%m')

    year, month = map(int, selected_monat.split('-'))
    month_start = date(year, month, 1)
    if month == 12:
        next_month_start = date(year + 1, 1, 1)
    else:
        next_month_start = date(year, month + 1, 1)

    selected_konto = request.GET.get('konto')
    selected_kategorie = request.GET.get('kategorie')
    search_query = request.GET.get('search')

    buchungen_qs = (
        Buchung.objects
        .filter(konto__benutzer=request.user)
        .select_related('konto', 'kategorie', 'vertrag')
        .order_by('-buchungsdatum')
    )

    if selected_konto:
        buchungen_qs = buchungen_qs.filter(konto__kontonummer=selected_konto)
    
    if selected_kategorie:
        buchungen_qs = buchungen_qs.filter(kategorie__kategorienummer=selected_kategorie)
    
    if search_query:
        buchungen_qs = buchungen_qs.filter(beschreibung__icontains=search_query)
    else:
        buchungen_qs = buchungen_qs.filter(
            buchungsdatum__gte=month_start,
            buchungsdatum__lt=next_month_start
        )
    
    buchungen = list(buchungen_qs)
    
    form_einnahme = BuchungEinnahmeForm(user=request.user)
    form_ausgabe = BuchungAusgabeForm(user=request.user)
    
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
            buchung = get_object_or_404(
                Buchung, pk=buchung_id, konto__benutzer=request.user
            )
            form = BuchungForm(request.POST, instance=buchung, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('buchung_list')
    
    context = {
        'buchungen': buchungen,
        'formularliste_bearbeiten': formularliste_bearbeiten,
        'form_einnahme': form_einnahme,
        'form_ausgabe': form_ausgabe,
        
        'konten': konten,
        'grouped_kategorien': grouped_kategorien,
        'selected_konto': selected_konto,
        'selected_kategorie': selected_kategorie,
        'selected_monat': selected_monat,
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



# Vertrag Views
@login_required
def vertrag_list(request):
    if request.method == 'POST':
        formtype = request.POST.get('formtype')
        if formtype == 'neu':
            form_new = VertragForm(request.POST, user=request.user)
            if form_new.is_valid():
                vertrag = form_new.save(commit=False)
                vertrag.benutzer = request.user
                vertrag.save()
                return redirect('vertrag_list')
        elif formtype == 'bearbeiten':
            vertrag_id = request.POST.get('vertrag_id')
            vertrag = get_object_or_404(Vertrag, pk=vertrag_id, benutzer=request.user)
            form_edit = VertragForm(request.POST, instance=vertrag, user=request.user)
            if form_edit.is_valid():
                form_edit.save()
                return redirect('vertrag_list')
        elif formtype == 'loeschen':
            vertrag_id = request.POST.get('vertrag_id')
            vertrag = get_object_or_404(Vertrag, pk=vertrag_id, benutzer=request.user)
            vertrag.delete()
            return redirect('vertrag_list')
    
    vertraege = Vertrag.objects.filter(benutzer=request.user).select_related('kategorie__hauptkategorie')
    
    ausgaben_list = []
    einnahmen_list = []
    sparen_list = []
    for vertrag in vertraege:
        form = VertragForm(instance=vertrag, user=request.user)
        hauptkat = vertrag.kategorie.hauptkategorie.name
        if hauptkat == "Einnahmen":
            einnahmen_list.append((vertrag, form))
        elif hauptkat == "Sparen":
            sparen_list.append((vertrag, form))
        else:
            ausgaben_list.append((vertrag, form))
    
    ausgaben_total = sum([vertrag.betrag for vertrag, _ in ausgaben_list])
    einnahmen_total = sum([vertrag.betrag for vertrag, _ in einnahmen_list])
    sparen_total = sum([vertrag.betrag for vertrag, _ in sparen_list])
    new_form = VertragForm(user=request.user)
    
    return render(request, 'core/vertrag_list.html', {
        'ausgaben_list': ausgaben_list,
        'einnahmen_list': einnahmen_list,
        'sparen_list': sparen_list,
        'new_form': new_form,
        'ausgaben_total': ausgaben_total,
        'einnahmen_total': einnahmen_total,
        'sparen_total': sparen_total,
    })

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
            print(form.errors)
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



# Konto Views
@login_required
def konto_list(request):
    konten = Konto.objects.filter(benutzer=request.user)
    
    form_create = KontoForm(user=request.user)
    formulare_bearbeiten = {}
    
    for k in konten:
        k.kontostand = k.berechne_kontostand()
        k.buchungen = Buchung.objects.filter(konto=k).order_by('-buchungsdatum')[:10]
        formulare_bearbeiten[k.kontonummer] = KontoForm(instance=k, user=request.user)
    
    context = {
        'konten': konten,
        'form_create': form_create,
        'formulare_bearbeiten': formulare_bearbeiten,
    }

    return render(request, 'core/konto_list.html', context)

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
    konto = get_object_or_404(Konto, pk=pk, benutzer=request.user)
    if request.method == 'POST':
        form = KontoForm(request.POST, instance=konto, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('konto_list')
    else:
        form = KontoForm(instance=konto, user=request.user)
    return render(request, 'core/konto_form.html', {'form': form})

@login_required
def konto_delete(request, pk):
    konto = get_object_or_404(Konto, pk=pk, benutzer=request.user)
    if request.method == 'POST':
        konto.delete()
        return redirect('konto_list')
    return render(request, 'core/konto_confirm_delete.html', {'konto': konto})



# Kategorie Views
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
            return redirect('einstellungen')
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
            return redirect('einstellungen')
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



# Budget Views
@login_required
def budget_list(request):
    monat = request.GET.get('monat')
    if monat:
        jahr, monat_num = map(int, monat.split('-'))
        aktueller_monat = date(jahr, monat_num, 1)
    else:
        aktueller_monat = date.today().replace(day=1)
    
    budgets = Budget.objects.filter(benutzer=request.user)
    form_create = BudgetForm(user=request.user)
    
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



# Statistik View
@login_required
def statistiken_view(request):
    today = date.today()
    
    months = []
    einnahmen = []
    ausgaben = []
    sparen_ausgaben = []
    
    for i in range(12):
        m = today.month - i
        y = today.year
        if m <= 0:
            m += 12
            y -= 1
    
        month_start = date(y, m, 1)
        if m == 12:
            next_month_start = date(y + 1, 1, 1)
        else:
            next_month_start = date(y, m + 1, 1)
    
        sum_einnahmen = (
            Buchung.objects
            .filter(konto__benutzer=request.user, buchungsart='Einnahme',
                    buchungsdatum__gte=month_start, buchungsdatum__lt=next_month_start)
            .aggregate(Sum('betrag'))['betrag__sum'] or 0
        )
    
        sum_ausgaben = (
            Buchung.objects
            .filter(konto__benutzer=request.user, buchungsart='Ausgabe',
                    buchungsdatum__gte=month_start, buchungsdatum__lt=next_month_start)
            .aggregate(Sum('betrag'))['betrag__sum'] or 0
        )
    
        sum_sparen = (
            Buchung.objects
            .filter(konto__benutzer=request.user, buchungsart='Ausgabe',
                    buchungsdatum__gte=month_start, buchungsdatum__lt=next_month_start,
                    kategorie__kategoriebezeichnung__iexact='Sparen')
            .aggregate(Sum('betrag'))['betrag__sum'] or 0
        )
    
        month_name = f"{calendar.month_abbr[m]} {y}"
        months.append(month_name)
        einnahmen.append(float(sum_einnahmen))
        ausgaben.append(float(sum_ausgaben))
        sparen_ausgaben.append(float(sum_sparen))
    
    months.reverse()
    einnahmen.reverse()
    ausgaben.reverse()
    sparen_ausgaben.reverse()
    
    current_month_start = date(today.year, today.month, 1)
    if today.month == 12:
        next_month_start = date(today.year + 1, 1, 1)
    else:
        next_month_start = date(today.year, today.month + 1, 1)
    
    unterkategorien = Kategorie.objects.filter(
        Q(benutzer=request.user) | Q(benutzer=None)
    ).select_related('hauptkategorie')
    
    from collections import defaultdict
    hauptkategorie_summen = defaultdict(float)
    
    for kat in unterkategorien:
        hauptname = kat.hauptkategorie.name if kat.hauptkategorie else None
    
        if hauptname in ["Einnahmen", "Sparen"]:
            continue
    
        summe = (
            Buchung.objects
            .filter(
                konto__benutzer=request.user,
                buchungsart='Ausgabe',
                buchungsdatum__gte=current_month_start,
                buchungsdatum__lt=next_month_start,
                kategorie=kat
            )
            .aggregate(Sum('betrag'))['betrag__sum'] or 0
        )
    
        if hauptname and summe > 0:
            hauptkategorie_summen[hauptname] += float(summe)
    
    pie_labels = list(hauptkategorie_summen.keys())
    pie_data = list(hauptkategorie_summen.values())
    if not pie_data:
        pie_labels = ["Keine Ausgaben"]
        pie_data = [0]
    
    context = {
        'months': months,
        'einnahmen': einnahmen,
        'ausgaben': ausgaben,
        'sparen_ausgaben': sparen_ausgaben,
        'pie_labels': pie_labels,
        'pie_data': pie_data,
    }
    
    return render(request, 'core/statistiken.html', context)



# Einstellungen View
@login_required
def einstellungen(request):
    if request.method == "POST":
        password_form = PasswordChangeForm(request.user, request.POST)
        if "change_password" in request.POST:
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                return redirect(reverse("einstellungen") + "?pwchanged=1")
    
    else:
        password_form = PasswordChangeForm(request.user)
    
    kategorien = Kategorie.objects.filter(benutzer=request.user)
    form_create_kategorie = KategorieForm(user=request.user)
    formulare_bearbeiten = { k.pk: KategorieForm(instance=k, user=request.user) for k in kategorien }
    
    return render(request, "core/einstellungen.html", {
        "password_form": password_form,
        "kategorien": kategorien,
        "form_create_kategorie": form_create_kategorie,
        "formulare_bearbeiten": formulare_bearbeiten,
    })
