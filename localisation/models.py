from django.db import models

class Localisation(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom de la localisation")
    latitude = models.FloatField(verbose_name="Latitude", blank=True, null=True)
    longitude = models.FloatField(verbose_name="Longitude", blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")

    def __str__(self):
        return f"{self.nom} ({self.latitude}, {self.longitude})"

class Itineraire(models.Model):
    depart = models.ForeignKey(Localisation, on_delete=models.CASCADE, related_name="depart_itineraires")
    arrivee = models.ForeignKey(Localisation, on_delete=models.CASCADE, related_name="arrivee_itineraires")
    distance = models.CharField(max_length=50, verbose_name="Distance")  # Exemple : "10 km"
    duree = models.CharField(max_length=50, verbose_name="Durée")  # Exemple : "15 min"
    points = models.TextField(verbose_name="Points de polyline")  # Encodage polyline pour la carte
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        return f"{self.depart.nom} → {self.arrivee.nom} ({self.distance}, {self.duree})"
