from django.urls import path
from .views import home, buchung_list, buchung_create, buchung_update, buchung_delete, konto_list, konto_create, konto_update, konto_delete, registrierung_view, login_view, logout_view, VertragsListeView

urlpatterns = [
    path('', login_view, name='home'),
    path('home/', home, name='home'),
    path('buchungen/', buchung_list, name='buchung_list'),
    path('buchungen/neu/', buchung_create, name='buchung_create'),
    path('registrierung/', registrierung_view, name='registrierung'),
    path('logout/', logout_view, name='logout'),
    path('vertraege/', VertragsListeView.as_view(), name='vertraege_liste'),
    path('buchungen/bearbeiten/<int:pk>/', buchung_update, name='buchung_update'),
    path('buchungen/loeschen/<int:pk>/', buchung_delete, name='buchung_delete'),
    path('konten/', konto_list, name='konto_list'),
    path('konten/neu/', konto_create, name='konto_create'),
    path('konten/bearbeiten/<int:pk>/', konto_update, name='konto_update'),
    path('konten/loeschen/<int:pk>/', konto_delete, name='konto_delete'),
]