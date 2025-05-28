from django.shortcuts import render, get_object_or_404, redirect
from QRCode.models import QRCode


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
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
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

