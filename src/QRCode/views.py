from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
import qrcode as qrcode_lib
from django.core.files.base import ContentFile
from io import BytesIO

from QRCode.models import QRCode

from django.utils.timezone import now
from datetime import timedelta
from tracking.models import Scan
from django.db.models import Count
import json

# Create your views here.
'''
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    target_url = models.URLField(max_length=500)
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
'''
def index(request):
    """
    View function for the home page of the site.
    """
    return render(request, 'QRCode/index.html')
def qr_code(request):

    # Check if user use the form to generate a QR code
    if request.method == 'POST':
        url = request.POST.get('target_url')
        title = request.POST.get('title')

        if url and title:
            print("Generating QR Code...")
            qr_code_obj = QRCode.objects.create(
                user=request.user,
                title=title,
                target_url=url,
                is_active=True
            )

            # Construire l'URL complète avec l'adresse IP
            ip_address = '192.168.1.149:8000'  # Remplacez par l'adresse IP de votre serveur
            qr_code_url = f'http://{ip_address}/access/{qr_code_obj.uuid}'

            # Génération de l'image du QR Code
            img = qrcode_lib.make(qr_code_url)
            buffer = BytesIO()
            img.save(buffer, format="PNG")

            # Sauvegarde dans ImageField
            filename = f"{qr_code_obj.uuid}.png"
            qr_code_obj.qr_image.save(filename, ContentFile(buffer.getvalue()), save=True)
        return redirect('qr_code')

    qrcodes = QRCode.objects.all()
    return render(request, 'QRCode/qrcode.html' ,context={ 'qrcodes': qrcodes} )


def qr_code_detail(request, uuid):
    qrcode = get_object_or_404(QRCode, uuid=uuid)

    # Check if user use the form to update the QR code
    if request.method == 'POST':
        url = request.POST.get('target_url')
        title = request.POST.get('title')

        if url and title:
            qrcode.target_url = url
            qrcode.title = title
            qrcode.updated_at = timezone.now()

            ip_address = '192.168.1.149:8000'  # Remplacez par l'adresse IP de votre serveur
            qr_code_url = f'http://{ip_address}/access/{qrcode.uuid}'

            # Regénère l'image QR code
            img = qrcode_lib.make(url)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            filename = f"{qrcode.uuid}.png"
            qrcode.qr_image.save(filename, ContentFile(buffer.getvalue()), save=True)

            qrcode.save()
            return redirect('qr_code_detail', uuid=qrcode.uuid)

    # Récupérer scans des 7 derniers jours pour ce QR code
    last_7_days = now().date() - timedelta(days=6)
    scans_by_day_qs = (
        Scan.objects.filter(qrcode=qrcode, timestamp__date__gte=last_7_days)
        .values('timestamp__date')
        .annotate(total=Count('id'))
        .order_by('timestamp__date')
    )

    scans_dict = {entry['timestamp__date'].isoformat(): entry['total'] for entry in scans_by_day_qs}

    labels = []
    data = []
    for i in range(7):
        day = (last_7_days + timedelta(days=i)).isoformat()
        labels.append(day)
        data.append(scans_dict.get(day, 0))

    return render(request, 'QRCode/detail.html', context={
        'qrcode': qrcode,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    })
def delete_qrcode(request,uuid):
    qrcode = get_object_or_404(QRCode, uuid=uuid)
    if qrcode:
        qrcode.delete()
        print("QR Code deleted successfully.")

    return redirect('qr_code')
