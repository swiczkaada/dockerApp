import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from QRCode.models import QRCode
from dockerApp.settings import FERNET_KEY, GEOIP_PATH
import geoip2.database

from tracking.utils import get_client_ip


# Create your views here.

def scan_redirect(request,uuid_str):
    """
    Logs a scan for the QR Code corresponding to the given UUID,
    then redirects to the target URL defined by the QR code.
    Redirects to the target URL if the QR Code is active,
    otherwise displays an error message.
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

    # Retrieve scan information
    ip = get_client_ip(request)

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')

    # Create the scan record
    qrcode.scans.create(
        ip_address=ip,
        user_agent=user_agent,
        referrer=referrer,
    )

    # Fallback security: if no target URL is set, redirect to homepage
    if not qrcode.target_url:
        return redirect('index')

    return redirect(qrcode.target_url)




