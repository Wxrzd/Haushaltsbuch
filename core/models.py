from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import timedelta, date

class BenutzerManager(BaseUserManager):
    def create_user(self, benutzername, email, passwort=None, **extra_fields):
        if not email:
            raise ValueError('Die E-Mail-Adresse muss angegeben werden')
        email = self.normalize_email(email)
        benutzer = self.model(benutzername=benutzername, email=email, **extra_fields)
        benutzer.set_password(passwort)
        benutzer.save(using=self._db)
        return benutzer

    def create_superuser(self, benutzername, email, passwort=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(benutzername, email, passwort, **extra_fields)

class Benutzer(AbstractBaseUser, PermissionsMixin):
    benutzername = models.CharField(max_length=150, unique=True, primary_key=True)
    email = models.EmailField(unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = BenutzerManager()

    USERNAME_FIELD = 'benutzername'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.benutzername


class Konto(models.Model):
    kontonummer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    kontotyp = models.CharField(max_length=50)
    benutzer = models.ForeignKey(Benutzer, on_delete=models.CASCADE)

    def berechne_kontostand(self):
        einnahmen = self.buchung_set.filter(buchungsart='Einnahme').aggregate(models.Sum('betrag'))['betrag__sum'] or 0
        ausgaben = self.buchung_set.filter(buchungsart='Ausgabe').aggregate(models.Sum('betrag'))['betrag__sum'] or 0
        return einnahmen - ausgaben

    def __str__(self):
        return self.name

class Hauptkategorie(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Kategorie(models.Model):
    kategorienummer = models.AutoField(primary_key=True)
    kategoriebezeichnung = models.CharField(max_length=100)
    hauptkategorie = models.ForeignKey(Hauptkategorie, on_delete=models.CASCADE, related_name='unterkategorien')
    benutzer = models.ForeignKey(Benutzer, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.hauptkategorie.name} > {self.kategoriebezeichnung}"

class Vertrag(models.Model):
    vertragsnummer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    startdatum = models.DateField(null=True)  # Neues Feld
    ablaufdatum = models.DateField()
    intervall = models.CharField(max_length=50)
    naechste_buchung = models.DateField(blank=True, null=True)  # Neues Feld

    benutzer = models.ForeignKey(Benutzer, on_delete=models.CASCADE)
    konto = models.ForeignKey(Konto, on_delete=models.CASCADE)
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.benutzer})"

    def berechne_naechste_buchung(self):
        """Berechnet die nächste Buchung basierend auf dem Intervall"""
        if self.intervall == "täglich":
            return self.startdatum + timedelta(days=1)
        elif self.intervall == "wöchentlich":
            return self.startdatum + timedelta(weeks=1)
        elif self.intervall == "monatlich":
            month = self.startdatum.month + 1
            year = self.startdatum.year
            if month > 12:
                month = 1
                year += 1
            return self.startdatum.replace(month=month, year=year)
        elif self.intervall == "jährlich":
            return self.startdatum.replace(year=self.startdatum.year + 1)
        return None  # Falls kein gültiges Intervall

    def save(self, *args, **kwargs):
        """Setzt automatisch die nächste Buchung beim Speichern"""
        if not self.naechste_buchung:
            self.naechste_buchung = self.berechne_naechste_buchung()
        super().save(*args, **kwargs)

    def erstelle_buchung(self):
        """Erstellt eine Buchung basierend auf dem Vertragsintervall"""
        if not self.naechste_buchung:
            return  # Falls keine nächste Buchung gesetzt wurde

        Buchung.objects.create(
            betrag=self.betrag,
            buchungsdatum=self.naechste_buchung,
            buchungsart="Ausgabe",
            konto=self.konto,
            vertrag=self,
            kategorie=self.kategorie
        )

        # Nächste Buchung neu berechnen
        self.naechste_buchung = self.berechne_naechste_buchung()
        self.save()

class Buchung(models.Model):
    BETRAGSTYPEN = (
        ('Einnahme', 'Einnahme'),
        ('Ausgabe', 'Ausgabe'),
    )
    
    buchungsnummer = models.AutoField(primary_key=True)
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    buchungsdatum = models.DateField()
    buchungsart = models.CharField(max_length=50, choices=BETRAGSTYPEN)
    beschreibung = models.TextField(null=True, blank=True)

    konto = models.ForeignKey(Konto, on_delete=models.CASCADE)
    vertrag = models.ForeignKey(Vertrag, on_delete=models.CASCADE, null=True, blank=True)
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE)

    def __str__(self):
        return f"Buchung {self.buchungsnummer}: {self.betrag} EUR, {self.buchungsart}"

class Budget(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    benutzer = models.ForeignKey(Benutzer, on_delete=models.CASCADE)
    kategorien = models.ManyToManyField(Kategorie)

    def berechne_ausgaben(self, monat: date = None):
        if monat is None:
            monat = date.today()
        start = monat.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)

        return Buchung.objects.filter(
            kategorie__in=self.kategorien.all(),
            buchungsart='Ausgabe',
            konto__benutzer=self.benutzer,
            buchungsdatum__gte=start,
            buchungsdatum__lt=end
        ).aggregate(models.Sum('betrag'))['betrag__sum'] or 0

    def restbetrag(self, monat: date = None):
        return self.betrag - self.berechne_ausgaben(monat)

    def __str__(self):
        return self.name
