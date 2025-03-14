from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Buchung, Nutzer

class RegistrierungsForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Nutzer
        fields = ['EMail', 'Benutzername', 'Passwort']

class LoginForm(AuthenticationForm):
    username = forms.EmailField()

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
