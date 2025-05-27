from django.db import models

from dockerApp.settings import FERNET_KEY

from cryptography.fernet import Fernet

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
    geo_data = models.JSONField(null=True, blank=True)

    fernet = Fernet(FERNET_KEY)

    def __str__(self):
        return f"Scan of {self.qrcode.title} at {self.timestamp} "

    def save(self, *args, **kwargs):
        # Chiffrer l'adresse IP et l'agent utilisateur avant de sauvegarder
        if self.ip_address:
            self.ip_address = self.encrypt(self.ip_address)
        if self.user_agent:
            self.user_agent = self.encrypt(self.user_agent)
        super().save(*args, **kwargs)

    def encrypt(self, data):
        """Chiffrer les données"""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, data):
        """Déchiffrer les données"""
        return self.fernet.decrypt(data.encode()).decode()
