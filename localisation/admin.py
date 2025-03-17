from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Localisation, Itineraire
import requests
import googlemaps
import polyline

class LocalisationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'latitude', 'longitude', 'voir_carte')
    readonly_fields = ('carte_interactive',)

    def voir_carte(self, obj):
        return mark_safe(f'<a href="https://www.google.com/maps?q={obj.latitude},{obj.longitude}" target="_blank">Voir sur Google Maps</a>')
    voir_carte.short_description = "Carte"

    def carte_interactive(self, obj=None):
        return mark_safe("""
            <div id="map" style="height: 400px;"></div>
            <script>
                function initMap() {
                    var map = new google.maps.Map(document.getElementById('map'), {
                        // Localisation de l'Hôtel Karavia à Lubumbashi
                        center: {lat: -11.6694, lng: 27.4792},
                        zoom: 15 // Vous pouvez ajuster le niveau de zoom si nécessaire
                    });

                    var marker = new google.maps.Marker({
                        position: {lat: -11.6694, lng: 27.4792},
                        map: map,
                        draggable: true
                    });

                    google.maps.event.addListener(marker, 'dragend', function (event) {
                        document.getElementById("id_latitude").value = event.latLng.lat();
                        document.getElementById("id_longitude").value = event.latLng.lng();
                    });

                    // Ajouter l'écouteur de clic pour remplir les champs
                    google.maps.event.addListener(map, 'click', function(event) {
                        var lat = event.latLng.lat();
                        var lng = event.latLng.lng();

                        // Mettre à jour la position du marqueur
                        marker.setPosition(event.latLng);

                        // Remplir les champs avec les coordonnées
                        document.getElementById("id_latitude").value = lat;
                        document.getElementById("id_longitude").value = lng;

                        // Optionnel : si vous voulez remplir aussi le champ 'nom', vous pouvez ajouter une logique pour cela
                        document.getElementById("id_nom").value = "Position: " + lat + ", " + lng; // Exemple de valeur pour le nom
                    });
                }
            </script>
            <script async defer src="https://maps.googleapis.com/maps/api/js?key={settings.GOOGLE_MAPS_API_KEY}&callback=initMap"></script>
        """)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)  # Sauvegarde l'objet dans la base de données
        print("Localisation enregistrée avec succès.", obj.id)
        # Envoi de la notification à l'API de notification
        try:
            api_url =  settings.NOTIFICATION_API_URL
            data = {
                'localisation_id': obj.id  # Passer l'ID de la localisation enregistrée
            }
            response = requests.post(api_url, json=data)

            if response.status_code == 200:
                print("Notification envoyée avec succès.")
            else:
                print(f"Erreur lors de l'envoi de la notification: {response.status_code}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de la notification: {str(e)}")


admin.site.register(Localisation, LocalisationAdmin)

@admin.register(Itineraire)
class ItineraireAdmin(admin.ModelAdmin):
    list_display = ('depart', 'arrivee', 'distance', 'duree', 'date_creation')
    list_filter = ('depart', 'arrivee')
    search_fields = ('depart__nom', 'arrivee__nom')
    date_hierarchy = 'date_creation'
    readonly_fields = ('Itineraire',)

    def Itineraire(self, obj):
        if not obj.points:
            return "Aucune donnée d'itinéraire disponible."

        decoded_points = polyline.decode(obj.points)
        points_js = ",\n".join([f"new google.maps.LatLng({lat}, {lng})" for lat, lng in decoded_points])

        html = f"""
        <div id="map" style="height: 400px;"></div>
        <script>
            function initMap() {{
                var map = new google.maps.Map(document.getElementById('map'), {{
                    center: new google.maps.LatLng({decoded_points[0][0]}, {decoded_points[0][1]}),
                    zoom: 12
                }});

                var path = [{points_js}];
                var polyline = new google.maps.Polyline({{
                    path: path,
                    geodesic: true,
                    strokeColor: "#FF0000",
                    strokeOpacity: 1.0,
                    strokeWeight: 5
                }});
                polyline.setMap(map);

                var startMarker = new google.maps.Marker({{
                    position: path[0],
                    map: map,
                    title: "Départ",
                    icon: "https://maps.google.com/mapfiles/kml/shapes/cabs.png"
                }});

                var endMarker = new google.maps.Marker({{
                    position: path[path.length - 1],
                    map: map,
                    title: "Arrivée",
                    icon: "https://maps.google.com/mapfiles/kml/paddle/A.png"
                }});
            }}
        </script>
        <script async defer src="https://maps.googleapis.com/maps/api/js?key={settings.GOOGLE_MAPS_API_KEY}&callback=initMap"></script>
        """

        return mark_safe(html)




