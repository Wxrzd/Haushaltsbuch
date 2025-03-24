from django.core.management.base import BaseCommand
from core.models import Hauptkategorie, Kategorie

STANDARD_KATEGORIEN = {
    "Drogerie": ["Drogerie"],
    "Einnahmen": ["Kapitalerträge", "Lohn / Gehalt", "Sonstige Einnahmen"],
    "Essen & Trinken": ["Lebensmittel", "Lieferservice", "Restaurants", "Mittagessen & Kantine"],
    "Finanzen": ["Steuern", "Bankgebühren"],
    "Freizeit": ["Bücher & Zeitungen", "Gaming", "Urlaub", "Sport", "Veranstaltungen"],
    "Gesundheit": ["Apotheke", "Ärztliche Behandlung"],
    "Lifestyle": ["Bekleidung", "Friseur", "Shopping", "Sonstiger Lifestyle"],
    "Mobilität": ["Auto", "Bus & Bahn"],
    "Sonstiges": ["Sonstige Ausgaben"],
    "Sparen": ["Sparen", "Kapitalanlage"],
    "Versicherungen": ["Haftpflichtversicherung", "Hausratversicherung"],
    "Wohnen": ["Miete", "Strom", "Internet & Telefon"],
}

class Command(BaseCommand):
    help = 'Erstellt oder aktualisiert die Standard-Haupt- und Unterkategorien'

    def handle(self, *args, **options):
        for haupt_name, unter_list in STANDARD_KATEGORIEN.items():
            hauptkat, _ = Hauptkategorie.objects.get_or_create(name=haupt_name)
            self.stdout.write(self.style.SUCCESS(f'Hauptkategorie: {haupt_name}'))

            for unter_name in unter_list:
                unterkat, created = Kategorie.objects.update_or_create(
                    hauptkategorie=hauptkat,
                    kategoriebezeichnung=unter_name,
                    benutzer=None,
                    defaults={'hauptkategorie': hauptkat}
                )
                action = "Erstellt" if created else "Aktualisiert"
                self.stdout.write(f"  {action}: {unter_name}")
