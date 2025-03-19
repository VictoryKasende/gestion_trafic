from django.urls import path
from .views import ObtenirItinerairesAPIView, ObtenirItinerairesParCoordonneesAPIView

urlpatterns = [
    path('obtenir-itineraires/', ObtenirItinerairesAPIView.as_view(), name="obtenir-itineraires"),
    path('itineraire-par-coordonnees/', ObtenirItinerairesParCoordonneesAPIView.as_view(),
         name='itineraire_par_coordonnees'),
]
