from rest_framework import serializers
from .models import Localisation, Itineraire

class LocalisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localisation
        fields = "__all__"

class ItineraireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itineraire
        fields = "__all__"

class ItineraireRequestSerializer(serializers.Serializer):
    depart = serializers.CharField(max_length=255)
    arrivee = serializers.CharField(max_length=255)
