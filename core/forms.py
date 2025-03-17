from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Buchung, Benutzer, Konto

class RegistrierungsForm(UserCreationForm):
    class Meta:
        model = Benutzer
        fields = ['email', 'benutzername', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Benutzer.objects.filter(email=email).exists():
            raise forms.ValidationError("Diese E-Mail-Adresse wird bereits verwendet.")
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Benutzername")

class BuchungForm(forms.ModelForm):
    buchungsdatum = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'datepicker',
            'value': date.today().strftime('%Y-%m-%d')  # Standardwert: Heute
        }),
        required=True
    )

    class Meta:
        model = Buchung
        fields = ['betrag', 'buchungsart', 'konto', 'vertrag', 'kategorie', 'buchungsdatum']
        
        widgets = {
            'buchungsart': forms.Select(choices=[('Einnahme', 'Einnahme'), ('Ausgabe', 'Ausgabe')]),
            'vertrag': forms.Select(),  # Falls optional, Dropdown lassen
            'kategorie': forms.Select(),
            'konto': forms.Select(),
        }

class KontoForm(forms.ModelForm):
    class Meta:
        model = Konto
        fields = ['name', 'kontotyp']  # 'benutzer' wird entfernt, da es automatisch gesetzt wird

    def __init__(self, *args, user=None, **kwargs):
        super(KontoForm, self).__init__(*args, **kwargs)
        self.user = user  # Speichert den angemeldeten Nutzer

    def save(self, commit=True):
        konto = super().save(commit=False)
        if self.user:
            konto.benutzer = self.user  # Setzt den angemeldeten Nutzer als Besitzer des Kontos
        if commit:
            konto.save()
        return konto
