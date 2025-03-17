from django.shortcuts import render, redirect
from .models import Buchung
from .forms import BuchungForm

def home(request):
    return render(request, 'core/home.html')

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