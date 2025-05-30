from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from QRCode.models import QRCode
from dockerApp.settings import FERNET_KEY, GEOIP_PATH
import geoip2.database

# Create your views here.

def scan_redirect(request,uuid_str):
    """
    Enregistre un scan pour le QR Code correspondant à l'UUID donné,
    puis redirige vers l'URL cible définie par le QR code.
    Redirige vers l'URL cible du QR Code si actif, sinon affiche un message d'erreur.
    """
    try:
        qrcode = QRCode.objects.get(uuid=uuid_str)
    except QRCode.DoesNotExist:
        return render(request, 'QRCode/invalid.html', {
            'message': "Ce QR code n'existe pas ou a été supprimé."
        })

    if not qrcode.is_active or not qrcode.user.is_active:
        return render(request, 'QRCode/invalid.html', {
            'message': "Ce QR code n'est plus valide ou a été désactivé."
        })



    # Récupération des infos du scan
    ip_header = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_header:
        ip = ip_header.split(',')[0].strip()  # Prend la première IP dans la liste
    else:
        ip = request.META.get('REMOTE_ADDR')

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')

    # Création du scan
    qrcode.scans.create(
        ip_address=ip,
        user_agent=user_agent,
        referrer=referrer,
    )

    # Sécurité : si aucune URL cible, on redirige vers une page de secours
    if not qrcode.target_url:
        return redirect('index')

    return redirect(qrcode.target_url)

def test_geoip_view(request):
    ip = request.GET.get('ip', '8.8.8.8')  # IP par défaut si pas précisée

    try:
        reader = geoip2.database.Reader(GEOIP_PATH + "/GeoLite2-City.mmdb")
        response = reader.city(ip)
        reader.close()

        result = (
            f"IP: {ip}<br>"
            f"Country: {response.country.name}<br>"
            f"City: {response.city.name}<br>"
            f"Region: {response.subdivisions.most_specific.name}<br>"
            f"Latitude: {response.location.latitude}<br>"
            f"Longitude: {response.location.longitude}<br>"
            f"Timezone: {response.location.time_zone}<br>"
        )
    except Exception as e:
        result = f"Erreur GeoIP: {e}"

    return HttpResponse(result)