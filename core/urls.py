from django.urls import path
from .views import home, buchung_list, buchung_create, buchung_update, buchung_delete, konto_list, konto_create, konto_update, konto_delete, registrierung_view, login_view, logout_view, vertrag_list, vertrag_create, vertrag_update, vertrag_delete, kategorie_list, kategorie_create, kategorie_update, kategorie_delete

urlpatterns = [
    path('', login_view, name='login'),
    path('home/', home, name='home'),
    path('buchungen/', buchung_list, name='buchung_list'),
    path('buchungen/neu/', buchung_create, name='buchung_create'),
    path('registrierung/', registrierung_view, name='registrierung'),
    path('logout/', logout_view, name='logout'),
    path('vertraege/', vertrag_list, name='vertrag_list'),
    path('vertraege/neu/', vertrag_create, name='vertrag_create'),
    path('vertraege/<int:pk>/bearbeiten/', vertrag_update, name='vertrag_update'),
    path('vertraege/<int:pk>/loeschen/', vertrag_delete, name='vertrag_delete'),
    path('buchungen/bearbeiten/<int:pk>/', buchung_update, name='buchung_update'),
    path('buchungen/loeschen/<int:pk>/', buchung_delete, name='buchung_delete'),
    path('konten/', konto_list, name='konto_list'),
    path('konten/neu/', konto_create, name='konto_create'),
    path('konten/bearbeiten/<int:pk>/', konto_update, name='konto_update'),
    path('konten/loeschen/<int:pk>/', konto_delete, name='konto_delete'),
    path('kategorien/', kategorie_list, name='kategorie_list'),
    path('kategorien/neu/', kategorie_create, name='kategorie_create'),
    path('kategorien/bearbeiten/<int:pk>/', kategorie_update, name='kategorie_update'),
    path('kategorien/loeschen/<int:pk>/', kategorie_delete, name='kategorie_delete'),
]