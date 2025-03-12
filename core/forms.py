from django import forms
from .models import Buchung

class BuchungForm(forms.ModelForm):
    class Meta:
        model = Buchung
        fields = ['Betrag', 'Buchungsart', 'KontoNr', 'VertragsNr', 'KategorieNr']  # Verwende die echten Spaltennamen!
        
        widgets = {
            'Buchungsart': forms.Select(choices=[('Einnahme', 'Einnahme'), ('Ausgabe', 'Ausgabe')]),
            'VertragsNr': forms.Select(),  # Falls optional, Dropdown lassen
            'KategorieNr': forms.Select(),
            'KontoNr': forms.Select(),
        }
