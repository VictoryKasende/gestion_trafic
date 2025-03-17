from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import googlemaps
import polyline
from django.conf import settings
from .models import Localisation, Itineraire
from .serializers import LocalisationSerializer, ItineraireSerializer, ItineraireRequestSerializer

API_KEY = settings.GOOGLE_MAPS_API_KEY
gmaps = googlemaps.Client(key=API_KEY)

class ObtenirItinerairesAPIView(APIView):
    def post(self, request):
        serializer = ItineraireRequestSerializer(data=request.data)
        if serializer.is_valid():
            depart_nom = serializer.validated_data["depart"]
            arrivee_nom = serializer.validated_data["arrivee"]

            depart, created_depart = Localisation.objects.get_or_create(nom=depart_nom)
            arrivee, created_arrivee = Localisation.objects.get_or_create(nom=arrivee_nom)

            # Récupérer les coordonnées si elles ne sont pas disponibles
            if not depart.latitude or not depart.longitude:
                coords = self.get_coordinates(depart_nom)
                if coords:
                    depart.latitude, depart.longitude = coords
                    depart.save()

            if not arrivee.latitude or not arrivee.longitude:
                coords = self.get_coordinates(arrivee_nom)
                if coords:
                    arrivee.latitude, arrivee.longitude = coords
                    arrivee.save()

            # Vérifier si on a bien les coordonnées
            if not depart.latitude or not depart.longitude or not arrivee.latitude or not arrivee.longitude:
                return Response({"message": "Impossible de récupérer les coordonnées."}, status=status.HTTP_400_BAD_REQUEST)

            # Obtenir les itinéraires
            directions = gmaps.directions(
                (depart.latitude, depart.longitude),
                (arrivee.latitude, arrivee.longitude),
                mode="driving",
                departure_time="now",
                alternatives=True
            )

            if not directions:
                return Response({"message": "Aucun itinéraire trouvé."}, status=status.HTTP_404_NOT_FOUND)

            # Trier et garder les 3 meilleurs itinéraires
            itineraires = sorted(
                directions,
                key=lambda r: r['legs'][0]['duration_in_traffic']['value']
            )[:3]

            itineraire_instances = []
            for itineraire in itineraires:
                itineraire_instance = Itineraire.objects.create(
                    depart=depart,
                    arrivee=arrivee,
                    distance=itineraire['legs'][0]['distance']['text'],
                    duree=itineraire['legs'][0]['duration_in_traffic']['text'],
                    points=itineraire['overview_polyline']['points']
                )
                itineraire_instances.append(itineraire_instance)

            return Response({
                "message": "Itinéraires obtenus et sauvegardés avec succès.",
                "itineraires": ItineraireSerializer(itineraire_instances, many=True).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_coordinates(self, location_name):
        """ Récupère les coordonnées GPS d'une localisation en utilisant l'API Google Maps """
        try:
            geocode_result = gmaps.geocode(location_name)
            if geocode_result and "geometry" in geocode_result[0]:
                location = geocode_result[0]["geometry"]["location"]
                return location["lat"], location["lng"]
        except Exception as e:
            print(f"Erreur lors de la récupération des coordonnées: {e}")
        return None
