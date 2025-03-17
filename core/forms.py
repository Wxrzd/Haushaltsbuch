from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Buchung, Benutzer, Konto, Vertrag, Kategorie

class RegistrierungsForm(UserCreationForm):
    class Meta:
        model = Benutzer
        fields = ['email', 'benutzername', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Benutzer.objects.filter(email=email).exists():
            raise forms.ValidationError("Diese E-Mail-Adresse wird bereits verwendet.")
        return email

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
    
    def __init__(self, *args, user=None, **kwargs):
        super(BuchungForm, self).__init__(*args, **kwargs)
        if user:
            # Zeige nur Konten des aktuell eingeloggten Benutzers an
            self.fields['konto'].queryset = Konto.objects.filter(benutzer=user)
            # Zeige nur Kategorien des aktuell eingeloggten Benutzers an
            self.fields['kategorie'].queryset = Kategorie.objects.filter(benutzer=user)
            # Zeige nur Verträge des aktuell eingeloggten Benutzers an
            self.fields['vertrag'].queryset = Vertrag.objects.filter(benutzer=user)

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

class VertragForm(forms.ModelForm):
    class Meta:
        model = Vertrag
        fields = ['name', 'betrag', 'ablaufdatum', 'intervall', 'konto', 'kategorie']
        widgets = {
            'ablaufdatum': forms.DateInput(attrs={'type': 'date'}),  # Kalenderfunktion
            'intervall': forms.Select(choices=[
                ('täglich', 'Täglich'),
                ('wöchentlich', 'Wöchentlich'),
                ('monatlich', 'Monatlich'),
                ('jährlich', 'Jährlich'),
            ]),
        }
    
class VertragForm(forms.ModelForm):
    class Meta:
        model = Vertrag
        fields = ['name', 'betrag', 'ablaufdatum', 'intervall', 'konto', 'kategorie']
        widgets = {
            'ablaufdatum': forms.DateInput(attrs={'type': 'date'}),  # Kalenderfunktion
            'intervall': forms.Select(choices=[
                ('täglich', 'Täglich'),
                ('wöchentlich', 'Wöchentlich'),
                ('monatlich', 'Monatlich'),
                ('jährlich', 'Jährlich'),
            ]),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)  # KORREKT für Python 3
        if user:
            # Filtere nur Konten des eingeloggten Benutzers
            self.fields['konto'].queryset = Konto.objects.filter(benutzer=user)
            # Filtere nur Kategorien des eingeloggten Benutzers
            self.fields['kategorie'].queryset = Kategorie.objects.filter(benutzer=user)

class KategorieForm(forms.ModelForm):
    class Meta:
        model = Kategorie
        fields = ['kategoriebezeichnung']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.instance.benutzer = user  # Benutzer automatisch setzen

