from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
import qrcode as qrcode_lib
from django.core.files.base import ContentFile
from io import BytesIO

from django.views.decorators.http import require_GET

from QRCode.decorators import qr_owner_or_admin_required
from QRCode.models import QRCode

from django.utils.timezone import now
from datetime import timedelta

from accounts.decorators import admin_or_superadmin_required
from activityLog.models import ActivityLog
from dockerApp.settings import MEDIA_ROOT
from tracking.models import Scan
from django.db.models import Count
import json
from django.db.models.functions import ExtractHour
import os
import re
from django.db.models import Q


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
    context = {}
    if request.user.is_authenticated:
        today = now().date()

        if request.user.is_superuser or request.user.is_admin():
            context['qrcodes'] = QRCode.objects.all().order_by('-created_at')[:5]
            context['total_qrcodes_today'] = QRCode.objects.filter(created_at__date=today).count()
            context['total_scans_today'] = Scan.objects.filter(timestamp__date=today).count()
            context['logs'] = ActivityLog.objects.filter(
                action_type__in=[
                    'USER_CREATED', 'USER_DEACTIVATED',
                    'USER_REACTIVATED', 'USER_DELETED'
                ],
                timestamp__date=today
            ).order_by('-timestamp')
            #context['latest_users'] = User.objects.order_by('-date_joined')[:5]
            # ajouter un form pour chercher un qrcode


        else:
            # Utilisateur classique
            context['my_qrcode_count'] = QRCode.objects.filter(user=request.user).count()
            context['last_qrcode'] = QRCode.objects.filter(user=request.user).order_by('-created_at').first()
            context['my_scans_today'] = Scan.objects.filter(qrcode__user=request.user, timestamp__date=today).count()

    return render(request, 'QRCode/index.html', context)

@login_required
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

            #Regiter the log
            ActivityLog.objects.create(
                user=request.user,
                action_type='QR_CREATED',
                description=f"QR Code créé : {title}",
                url = qr_code_obj.target_url
            )
        return redirect('qr_code')

    # Les qr codes de l'utilisateur connecté (id) user_id

    qrcodes = QRCode.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'QRCode/qrcode.html' ,context={ 'qrcodes': qrcodes} )

#Seul l'user de ce qr code peuvt acceder ou soit c'est un admin ou super admin

@qr_owner_or_admin_required
@login_required
def qr_code_detail(request, qrcode):
    #qrcode = get_object_or_404(QRCode, uuid=uuid)


    # Update QR code via form
    if request.method == 'POST':
        url = request.POST.get('target_url')
        title = request.POST.get('title')
        is_active = request.POST.get('is_active') == 'on'

        if url and title:
            qrcode.target_url = url
            qrcode.title = title
            qrcode.is_active = is_active
            qrcode.updated_at = now()

            ip_address = '192.168.1.149:8000'  # Remplace par ton IP réelle
            qr_code_url = f'http://{ip_address}/access/{qrcode.uuid}'

            # Regenerate QR code image
            img = qrcode_lib.make(qr_code_url)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            filename = f"{qrcode.uuid}.png"
            qrcode.qr_image.save(filename, ContentFile(buffer.getvalue()), save=False)

            qrcode.save()
            # Register the log
            ActivityLog.objects.create(
                user=request.user,
                action_type='QR_UPDATED',
                description=f"QR Code mis à jour : {title}",
                url=qrcode.target_url
            )
            return redirect('qr_code_detail', uuid=qrcode.uuid)

    # Stats - Scans sur les 7 derniers jours
    today = now().date()
    last_7_days = today - timedelta(days=6)

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

    # Stats - Scans par heure
    scans_by_hour_qs = (
        Scan.objects.filter(qrcode=qrcode)
        .annotate(hour=ExtractHour('timestamp'))
        .values('hour')
        .annotate(total=Count('id'))
        .order_by('hour')
    )

    hour_dict = {entry['hour']: entry['total'] for entry in scans_by_hour_qs}
    hour_labels = list(range(24))
    hour_data = [hour_dict.get(h, 0) for h in hour_labels]

    return render(request, 'QRCode/detail.html', {
        'qrcode': qrcode,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'hour_labels': json.dumps(hour_labels),
        'hour_data': json.dumps(hour_data),
    })

@qr_owner_or_admin_required
@login_required
def delete_qrcode(request,qrcode):
    #qrcode = get_object_or_404(QRCode, uuid=uuid)

    # Dossier où les images QR sont stockées
    qr_dir = os.path.join(MEDIA_ROOT, 'qrcodes')  # adapte si tu stockes ailleurs

    # Pattern strict : commence par uuid, suivi de _optionnel ou rien, puis .png
    pattern = re.compile(rf"^{re.escape(str(qrcode.uuid))}(_[^/\\]+)?\.png$")

    if os.path.exists(qr_dir):
        for filename in os.listdir(qr_dir):
            if pattern.match(filename):
                file_path = os.path.join(qr_dir, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

    if qrcode:
        qrcode.delete()
        # Register the log
        ActivityLog.objects.create(
            user=request.user,
            action_type='QR_DELETED',
            description=f"QR Code effacé : {qrcode.title}",
            url=qrcode.target_url
        )
        print("QR Code deleted successfully.")

    return redirect('qr_code')

@qr_owner_or_admin_required
@login_required
def reload_qrcode_image(request, qrcode):
    #qrcode = get_object_or_404(QRCode, uuid=uuid)

    if qrcode.target_url:
        ip_address = '192.168.1.149:8000'  # Remplace par ton IP réelle
        qr_code_url = f'http://{ip_address}/access/{qrcode.uuid}'
        # Générer une nouvelle image QR Code
        img = qrcode_lib.make(qr_code_url)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        filename = f"{qrcode.uuid}.png"
        qrcode.qr_image.save(filename, ContentFile(buffer.getvalue()), save=False)
        qrcode.updated_at = timezone.now()
        qrcode.save()

    return redirect('qr_code_detail', uuid=qrcode.uuid)




@require_GET
@admin_or_superadmin_required
def search_qrcodes(request):
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('type', '').strip()
    status = request.GET.get('status', 'all').strip()

    if not query or not search_type:
        return JsonResponse([], safe=False)

    filters = Q()
    if search_type == "uuid":
        filters = Q(uuid__icontains=query)
    elif search_type == "title":
        filters = Q(title__icontains=query)
    elif search_type == "url":
        filters = Q(target_url__icontains=query)
    else:
        return JsonResponse([], safe=False)  # Critère non reconnu

    if status == "active":
        filters &= Q(is_active=True)
    elif status == "inactive":
        filters &= Q(is_active=False)

    qrcodes = QRCode.objects.filter(filters)
    results = [
        {
            'title': qr.title,
            'target_url': qr.target_url,
            'scan_count': qr.scan_count,
            'uuid': str(qr.uuid),
        }
        for qr in qrcodes
    ]

    return JsonResponse(results, safe=False)
