from django import forms
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django import forms
from itertools import groupby
from operator import attrgetter
from .models import Buchung, Benutzer, Konto, Vertrag, Kategorie, Budget
from django.utils.timezone import now

def get_kategorie_choices(user):
    from .models import Hauptkategorie, Kategorie
    from django.db.models import Q

    hauptkategorien = Hauptkategorie.objects.all()
    kategorien = Kategorie.objects.filter(Q(benutzer=user) | Q(benutzer=None)).select_related('hauptkategorie')

    grouped_choices = []
    for haupt in hauptkategorien:
        unterkats = kategorien.filter(hauptkategorie=haupt)
        if unterkats.exists():
            grouped_choices.append((
                haupt.name,
                [(kat.pk, kat.kategoriebezeichnung) for kat in unterkats]
            ))
    return grouped_choices

class GroupedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, group_by_field, group_label=None, *args, **kwargs):
        self.group_by_field = group_by_field
        self.group_label = group_label or (lambda group: str(group))
        super().__init__(*args, **kwargs)

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return self._build_grouped_choices()
    
    @property
    def choices(self):
        return self._build_grouped_choices()

    @choices.setter
    def choices(self, value):
        self._choices = value

    def _build_grouped_choices(self):
        if self.queryset is None:
            return []
        choices = []
        queryset = list(self.queryset.all())
        queryset.sort(key=lambda obj: getattr(obj, self.group_by_field).name)
        for group, items in groupby(queryset, key=attrgetter(self.group_by_field)):
            group_label = self.group_label(group)
            group_choices = [(self.prepare_value(item), self.label_from_instance(item)) for item in items]
            choices.append((group_label, group_choices))
        return choices

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
            self.fields['kategorie'].choices = get_kategorie_choices(user)
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
        self.instance.buchungsart = 'Einnahme'
        if user:
            self.fields['konto'].queryset = Konto.objects.filter(benutzer=user)
            self.fields['kategorie'].choices = get_kategorie_choices(user)
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
        self.instance.buchungsart = 'Ausgabe'
        if user:
            self.fields['konto'].queryset = Konto.objects.filter(benutzer=user)
            self.fields['kategorie'].choices = get_kategorie_choices(user)
            self.fields['vertrag'].queryset = Vertrag.objects.filter(benutzer=user)

class KontoForm(forms.ModelForm):
    class Meta:
        model = Konto
        fields = ['name', 'kontotyp']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'kontotyp': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
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
    startdatum = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'},  
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        required=False
    )
    ablaufdatum = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date'},
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        required=False
    )

    class Meta:
        model = Vertrag
        fields = ['name', 'betrag', 'startdatum', 'ablaufdatum', 'intervall', 'konto', 'kategorie']
        widgets = {
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
            self.fields['kategorie'].choices = get_kategorie_choices(user)

class KategorieForm(forms.ModelForm):
    class Meta:
        model = Kategorie
        fields = ['hauptkategorie', 'kategoriebezeichnung']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.instance.benutzer = user

class BudgetForm(forms.ModelForm):
    kategorien = forms.ModelMultipleChoiceField(
        queryset=Kategorie.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Budget
        fields = ['name', 'betrag', 'kategorien']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['kategorien'].queryset = Kategorie.objects.filter(
                Q(benutzer=user) | Q(benutzer=None)
            ).select_related('hauptkategorie').order_by('hauptkategorie__name', 'kategoriebezeichnung')
            self.instance.benutzer = user

