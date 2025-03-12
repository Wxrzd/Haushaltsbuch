from django.urls import path
from .views import home, buchung_list, buchung_create

urlpatterns = [
    path('', home, name='home'),
    path('buchungen/', buchung_list, name='buchung_list'),
    path('buchungen/neu/', buchung_create, name='buchung_create'),
]
