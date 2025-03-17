from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import datetime, timedelta


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

class Kategorie(models.Model):
    kategorienummer = models.AutoField(primary_key=True)
    kategoriebezeichnung = models.CharField(max_length=100)
    benutzer = models.ForeignKey(Benutzer, on_delete=models.CASCADE)

    def __str__(self):
        return self.kategoriebezeichnung

class Vertrag(models.Model):
    vertragsnummer = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    ablaufdatum = models.DateField()
    intervall = models.CharField(max_length=50)
    
    benutzer = models.ForeignKey(Benutzer, on_delete=models.CASCADE)
    konto = models.ForeignKey(Konto, on_delete=models.CASCADE)
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.benutzer})"

    def erstelle_buchung(self):
        """Erstellt eine Buchung basierend auf dem Vertragsintervall"""
        if self.intervall == "täglich":
            naechstes_datum = self.ablaufdatum + timedelta(days=1)
        elif self.intervall == "wöchentlich":
            naechstes_datum = self.ablaufdatum + timedelta(weeks=1)
        elif self.intervall == "monatlich":
            # Logik für Monate ohne `relativedelta`
            month = self.ablaufdatum.month + 1
            year = self.ablaufdatum.year
            if month > 12:
                month = 1
                year += 1
            naechstes_datum = self.ablaufdatum.replace(month=month, year=year)
        elif self.intervall == "jährlich":
            naechstes_datum = self.ablaufdatum.replace(year=self.ablaufdatum.year + 1)
        else:
            return  # Keine automatische Buchung für unbekannte Intervalle

        Buchung.objects.create(
            betrag=self.betrag,
            buchungsdatum=naechstes_datum,
            buchungsart="Ausgabe",  # Verträge sind normalerweise Ausgaben
            konto=self.konto,
            vertrag=self,
            kategorie=self.kategorie
        )


class Buchung(models.Model):
    BETRAGSTYPEN = (
        ('Einnahme', 'Einnahme'),
        ('Ausgabe', 'Ausgabe'),
    )
    
    buchungsnummer = models.AutoField(primary_key=True)
    betrag = models.DecimalField(max_digits=10, decimal_places=2)
    buchungsdatum = models.DateField()
    buchungsart = models.CharField(max_length=50, choices=BETRAGSTYPEN)

    konto = models.ForeignKey(Konto, on_delete=models.CASCADE)
    vertrag = models.ForeignKey(Vertrag, on_delete=models.CASCADE, null=True, blank=True)
    kategorie = models.ForeignKey(Kategorie, on_delete=models.CASCADE)

    def __str__(self):
        return f"Buchung {self.buchungsnummer}: {self.betrag} EUR, {self.buchungsart}"
