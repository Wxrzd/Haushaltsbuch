from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class NutzerManager(BaseUserManager):
    def create_user(self, Benutzername, EMail, Passwort=None, **extra_fields):
        if not EMail:
            raise ValueError('Die E-Mail-Adresse muss angegeben werden')
        email = self.normalize_email(EMail)
        user = self.model(Benutzername=Benutzername, EMail=email, **extra_fields)
        user.set_password(Passwort)
        user.save(using=self._db)
        return user

    def create_superuser(self, Benutzername, EMail, Passwort=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(Benutzername, EMail, Passwort, **extra_fields)


class Nutzer(AbstractBaseUser, PermissionsMixin):
    Benutzername = models.CharField(max_length=150, unique=True)
    EMail = models.EmailField(unique=True)
    Passwort = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = NutzerManager()

    USERNAME_FIELD = 'Benutzername'
    EMAIL_FIELD = 'EMail'
    REQUIRED_FIELDS = ['EMail']

    def __str__(self):
        return self.Benutzername

class Konto(models.Model):
    KontoNr = models.AutoField(primary_key=True)  
    Kontobezeichnung = models.CharField(max_length=100, db_column='Kontobezeichnung')
    Kontotyp = models.CharField(max_length=50, db_column='Kontotyp')
    Kontostand = models.DecimalField(max_digits=10, decimal_places=2, db_column='Kontostand')
    Benutzername = models.ForeignKey(Nutzer, on_delete=models.CASCADE, db_column='Benutzername')

    class Meta:
        db_table = 'Konto'  # Stellt sicher, dass Django die bestehende MySQL-Tabelle nutzt

    def __str__(self):
        return self.Kontobezeichnung

class Kategorie(models.Model):
    class Meta:
        db_table = "Kategorie"  # Setzt den exakten Tabellennamen in MySQL

    KategorieNr = models.AutoField(primary_key=True)
    Kategoriebezeichnung = models.CharField(max_length=100, db_column='Kategoriebezeichnung')

class Vertrag(models.Model):
    class Meta:
        db_table = "Vertrag"  # Setzt den exakten Tabellennamen in MySQL

    VertragsNr = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100, db_column='Name')
    Betrag = models.DecimalField(max_digits=10, decimal_places=2, db_column="Betrag")
    Ablaufdatum = models.DateField(db_column="Ablaufdatum")
    Intervall = models.CharField(max_length=50, db_column="Intervall")
    Benutzernahme = models.ForeignKey(Nutzer, on_delete=models.CASCADE, db_column='Benutzername')
    KontoNr = models.ForeignKey(Konto, on_delete=models.CASCADE, db_column='KontoNr')
    KategorieNr = models.ForeignKey('Kategorie', on_delete=models.CASCADE, db_column='KategorieNr')

class Buchung(models.Model):
    class Meta:
        db_table = "Buchung"  # Setzt den exakten Tabellennamen in MySQL
    
    BETRAGSTYPEN = (
        ('Einnahme', 'Einnahme'),
        ('Ausgabe', 'Ausgabe'),
    )
    
    BuchungsNr = models.AutoField(primary_key=True)
    Betrag = models.DecimalField(max_digits=10, decimal_places=2)
    Buchungsart = models.CharField(max_length=50)

    KontoNr = models.ForeignKey(Konto, on_delete=models.CASCADE, db_column='KontoNr')
    VertragsNr = models.ForeignKey('Vertrag', on_delete=models.CASCADE, db_column='VertragsNr', null=True, blank=True)
    KategorieNr = models.ForeignKey('Kategorie', on_delete=models.CASCADE, db_column='KategorieNr')

    def __str__(self):
        return f"Buchung {self.BuchungsNr}: {self.Betrag} EUR, {self.Buchungsart}"
    


