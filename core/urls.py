from django.urls import path
from .views import home, buchung_list, buchung_create, konto_list, konto_create, konto_update, konto_delete

urlpatterns = [
    path('', home, name='home'),
    path('buchungen/', buchung_list, name='buchung_list'),
    path('buchungen/neu/', buchung_create, name='buchung_create'),
    path('konten/', konto_list, name='konto_list'),
    path('konten/neu/', konto_create, name='konto_create'),
    path('konten/bearbeiten/<int:pk>/', konto_update, name='konto_update'),
    path('konten/loeschen/<int:pk>/', konto_delete, name='konto_delete'),
]
