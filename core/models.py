from django.db import models

class Nutzer(models.Model):
    Benutzername = models.CharField(max_length=100, primary_key=True, db_column='Benutzername')
    Email = models.CharField(max_length=100, db_column='Email')
    Passwort = models.CharField(max_length=100, db_column='Passwort')

    class Meta:
        db_table = 'Nutzer'

    def __str__(self):
        return self.Benutzername

class Konto(models.Model):
    KontoNr = models.AutoField(primary_key=True)  
    Kontobezeichnung = models.CharField(max_length=100, db_column='Kontobezeichnung')
    Kontotyp = models.CharField(max_length=50, db_column='Kontotyp')
    Benutzername = models.ForeignKey(Nutzer, on_delete=models.CASCADE, db_column='Benutzername')

    class Meta:
        db_table = 'Konto'

    def berechne_kontostand(self):
        einnahmen = self.buchung_set.filter(Buchungsart='Einnahme').aggregate(models.Sum('Betrag'))['Betrag__sum'] or 0
        ausgaben = self.buchung_set.filter(Buchungsart='Ausgabe').aggregate(models.Sum('Betrag'))['Betrag__sum'] or 0
        return einnahmen - ausgaben

    def __str__(self):
        return self.Kontobezeichnung

class Kategorie(models.Model):
    class Meta:
        db_table = "Kategorie"  # Setzt den exakten Tabellennamen in MySQL

    KategorieNr = models.AutoField(primary_key=True)
    Kategoriebezeichnung = models.CharField(max_length=100, db_column='Kategoriebezeichnung')
    Benutzername = models.ForeignKey(Nutzer, on_delete=models.CASCADE, db_column='Benutzername')

    def __str__(self):
        return self.Kategoriebezeichnung

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

    def __str__(self):
        return self.Name

class Buchung(models.Model):
    class Meta:
        db_table = "Buchung"  # Setzt den exakten Tabellennamen in MySQL
    
    BETRAGSTYPEN = (
        ('Einnahme', 'Einnahme'),
        ('Ausgabe', 'Ausgabe'),
    )
    
    BuchungsNr = models.AutoField(primary_key=True)
    Betrag = models.DecimalField(max_digits=10, decimal_places=2)
    Buchungsdatum = models.DateField()
    Buchungsart = models.CharField(max_length=50)

    KontoNr = models.ForeignKey(Konto, on_delete=models.CASCADE, db_column='KontoNr')
    VertragsNr = models.ForeignKey('Vertrag', on_delete=models.CASCADE, db_column='VertragsNr', null=True, blank=True)
    KategorieNr = models.ForeignKey('Kategorie', on_delete=models.CASCADE, db_column='KategorieNr')

    def __str__(self):
        return f"Buchung {self.BuchungsNr}: {self.Betrag} EUR, {self.Buchungsart}"
    


