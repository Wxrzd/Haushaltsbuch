from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from .models import Buchung, Benutzer, Konto, Vertrag, Kategorie, Budget
from django.utils.timezone import now

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
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'datepicker'
            },
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        initial=now().date,
        required=True
    )

    class Meta:
        model = Buchung
        fields = [
            'buchungsdatum',
            'betrag',
            'beschreibung',
            'kategorie',
            'konto',
            'vertrag',
            'buchungsart',
        ]
        widgets = {
            'buchungsart': forms.Select(choices=[('Einnahme', 'Einnahme'), ('Ausgabe', 'Ausgabe')]),
            'beschreibung': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['konto'].queryset = Konto.objects.filter(benutzer=user)
            self.fields['kategorie'].queryset = Kategorie.objects.filter(benutzer=user)
            self.fields['vertrag'].queryset = Vertrag.objects.filter(benutzer=user)

class BuchungEinnahmeForm(forms.ModelForm):
    """
    Formular speziell für Einnahmen (Buchungsart=Einnahme).
    """
    buchungsdatum = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'datepicker',
            'value': date.today().strftime('%Y-%m-%d')
        }),
        required=True
    )

    class Meta:
        model = Buchung
        fields = [
            'buchungsdatum',
            'betrag',
            'beschreibung',
            'kategorie',
            'konto',
            'vertrag',
        ]
        widgets = {
            'beschreibung': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Buchungsart wird fest auf Einnahme gesetzt
        self.instance.buchungsart = 'Einnahme'
        if user:
            self.fields['konto'].queryset = Konto.objects.filter(benutzer=user)
            self.fields['kategorie'].queryset = Kategorie.objects.filter(benutzer=user)
            self.fields['vertrag'].queryset = Vertrag.objects.filter(benutzer=user)

class BuchungAusgabeForm(forms.ModelForm):
    """
    Formular speziell für Ausgaben (Buchungsart=Ausgabe).
    """
    buchungsdatum = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'datepicker',
            'value': date.today().strftime('%Y-%m-%d')
        }),
        required=True
    )

    class Meta:
        model = Buchung
        fields = [
            'buchungsdatum',
            'betrag',
            'beschreibung',
            'kategorie',
            'konto',
            'vertrag',
        ]
        widgets = {
            'beschreibung': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Buchungsart wird fest auf Ausgabe gesetzt
        self.instance.buchungsart = 'Ausgabe'
        if user:
            self.fields['konto'].queryset = Konto.objects.filter(benutzer=user)
            self.fields['kategorie'].queryset = Kategorie.objects.filter(benutzer=user)
            self.fields['vertrag'].queryset = Vertrag.objects.filter(benutzer=user)

class KontoForm(forms.ModelForm):
    class Meta:
        model = Konto
        fields = ['name', 'kontotyp']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        konto = super().save(commit=False)
        if self.user:
            konto.benutzer = self.user
        if commit:
            konto.save()
        return konto

class VertragForm(forms.ModelForm):
    class Meta:
        model = Vertrag
        fields = ['name', 'betrag', 'ablaufdatum', 'intervall', 'konto', 'kategorie']
        widgets = {
            'ablaufdatum': forms.DateInput(attrs={'type': 'date'}),
            'intervall': forms.Select(choices=[
                ('täglich', 'Täglich'),
                ('wöchentlich', 'Wöchentlich'),
                ('monatlich', 'Monatlich'),
                ('jährlich', 'Jährlich'),
            ]),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['konto'].queryset = Konto.objects.filter(benutzer=user)
            self.fields['kategorie'].queryset = Kategorie.objects.filter(benutzer=user)

class KategorieForm(forms.ModelForm):
    class Meta:
        model = Kategorie
        fields = ['kategoriebezeichnung']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.instance.benutzer = user

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'betrag', 'kategorien']
        widgets = {
            'kategorien': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['kategorien'].queryset = Kategorie.objects.filter(benutzer=user)
            self.instance.benutzer = user