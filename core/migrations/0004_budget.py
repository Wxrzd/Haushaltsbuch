# Generated by Django 5.1.7 on 2025-03-23 15:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_buchung_beschreibung'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('betrag', models.DecimalField(decimal_places=2, max_digits=10)),
                ('monat', models.DateField()),
                ('benutzer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('kategorien', models.ManyToManyField(to='core.kategorie')),
            ],
        ),
    ]
