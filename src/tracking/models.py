from django.db import models

from django.conf import settings
from dockerApp.settings import FERNET_KEY, GEOIP_PATH

from cryptography.fernet import Fernet
import geoip2.database
# Create your models here.
'''
Champ	Type	Description
qrcode	ForeignKey vers QRCode	Le QR code qui a été scanné
timestamp	DateTimeField	Date et heure du scan
ip_address	CharField (ou générique)	Adresse IP de la personne qui scanne
user_agent	TextField	Données du navigateur/appareil
referrer	URLField (optionnel)	Lien précédent (si le scan a été cliqué depuis un lien)
geo_data	JSONField (optionnel)	Pour stocker des infos de géoloc, si tu l’ajoutes plus tard
'''


class Scan(models.Model):
    qrcode = models.ForeignKey('QRCode.QRCode', on_delete=models.CASCADE, related_name='scans')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)

    # Décomposition de geo_data
    geo_ip = models.GenericIPAddressField(null=True, blank=True)
    geo_country = models.CharField(max_length=100, null=True, blank=True)
    geo_city = models.CharField(max_length=100, null=True, blank=True)
    geo_region = models.CharField(max_length=100, null=True, blank=True)
    geo_latitude = models.FloatField(null=True, blank=True)
    geo_longitude = models.FloatField(null=True, blank=True)
    geo_timezone = models.CharField(max_length=100, null=True, blank=True)


    fernet = Fernet(FERNET_KEY)

    def __str__(self):
        return f"Scan of {self.qrcode.title} at {self.timestamp} "


    def save(self, *args, **kwargs):
        raw_ip = self.ip_address

        if raw_ip:
            geo_info = self.get_geo_info(raw_ip)

            self.geo_ip = raw_ip
            self.geo_country = geo_info.get("country")
            self.geo_city = geo_info.get("city")
            self.geo_region = geo_info.get("region")
            self.geo_latitude = geo_info.get("latitude")
            self.geo_longitude = geo_info.get("longitude")
            self.geo_timezone = geo_info.get("timezone")

            # Chiffre l'adresse IP avant de stocké
            self.ip_address = self.encrypt(raw_ip)

        if self.user_agent:
            self.user_agent = self.encrypt(self.user_agent)

        super().save(*args, **kwargs)


    def encrypt(self, data):
        """Chiffrer les données"""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data):
        """Déchiffrer les données"""
        return self.fernet.decrypt(data.encode()).decode()

    def get_geo_info(self, ip):
        try:
            reader = geoip2.database.Reader(GEOIP_PATH + "/GeoLite2-City.mmdb")
            response = reader.city(ip)
            reader.close()

            return {
                "country": response.country.name,
                "city": response.city.name,
                "region": response.subdivisions.most_specific.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "timezone": response.location.time_zone,
            }
        except Exception as e:
            return {}