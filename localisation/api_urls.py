from django.urls import path
from .views import ObtenirItinerairesAPIView

urlpatterns = [
    path('obtenir-itineraires/', ObtenirItinerairesAPIView.as_view(), name="obtenir-itineraires"),
]