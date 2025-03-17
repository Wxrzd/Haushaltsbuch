from django.urls import path
from .views import home, buchung_list, buchung_create
from .views import registrierung_view, login_view, logout_view, VertragsListeView

urlpatterns = [
    path('', home, name='home'),
    path('buchungen/', buchung_list, name='buchung_list'),
    path('buchungen/neu/', buchung_create, name='buchung_create'),
    path('registrierung/', registrierung_view, name='registrierung'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('vertraege/', VertragsListeView.as_view(), name='vertraege_liste'),
]
