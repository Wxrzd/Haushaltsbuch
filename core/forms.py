from django import forms
from datetime import date
from .models import Buchung, Konto

class BuchungForm(forms.ModelForm):
    Buchungsdatum = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'datepicker',
            'value': date.today().strftime('%Y-%m-%d')  # Standardwert: Heute
        }),
        required=True
    )

    class Meta:
        model = Buchung
        fields = ['Betrag', 'Buchungsart', 'KontoNr', 'VertragsNr', 'KategorieNr', 'Buchungsdatum']  # Datum ist jetzt verpflichtend
        
        widgets = {
            'Buchungsart': forms.Select(choices=[('Einnahme', 'Einnahme'), ('Ausgabe', 'Ausgabe')]),
            'VertragsNr': forms.Select(),  # Falls optional, Dropdown lassen
            'KategorieNr': forms.Select(),
            'KontoNr': forms.Select(),
        }

class KontoForm(forms.ModelForm):
    class Meta:
        model = Konto
        fields = ['Kontobezeichnung', 'Kontotyp', 'Benutzername']