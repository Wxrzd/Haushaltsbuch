from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Buchung, Nutzer, Konto

class RegistrierungsForm(UserCreationForm):
    class Meta:
        model = Nutzer
        fields = ['EMail', 'Benutzername', 'password1', 'password2']
    
    def clean_EMail(self):
        email = self.cleaned_data.get('EMail')
        if Nutzer.objects.filter(EMail=email).exists():
            raise forms.ValidationError("Diese E-Mail-Adresse wird bereits verwendet.")
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Benutzername")

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