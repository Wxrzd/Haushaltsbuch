# Generated by Django 5.1.7 on 2025-04-02 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_vertrag_naechste_buchung_vertrag_startdatum'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vertrag',
            name='naechste_buchung',
        ),
    ]
