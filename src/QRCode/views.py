import os
import re
import json
from io import BytesIO
from datetime import timedelta


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Count, Q
from django.db.models.functions import ExtractHour
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET

import qrcode as qrcode_lib
from django.core.files.base import ContentFile

from QRCode.decorators import qr_owner_or_admin_required
from QRCode.models import QRCode
from activityLog.models import ActivityLog
from tracking.models import Scan
from accounts.decorators import admin_or_superadmin_required
from dockerApp.settings import MEDIA_ROOT

# Environment variables for dynamic URL building
DOMAIN = os.environ.get('DOMAIN_IP') or 'localhost'
DOMAIN_NGROK = os.environ.get('DOMAIN_NGROK')
PORT = os.environ.get('PORT', '8000')  # Default to 8000 if PORT is not set
PROTOCOL = os.environ.get('PROTOCOL', 'http')
DOMAIN_PROD = os.environ.get('DOMAIN_PROD')
PROTOCOL_PROD = os.environ.get('PROTOCOL_PROD')


def index(request):
    """
    Dashboard view:
    - Shows recent QR codes, scans, and logs for admin users.
    - Shows user's QR code stats for regular users.
    """
    context = {}
    if request.user.is_authenticated:
        today = now().date()

        if request.user.is_superuser or request.user.is_admin():
            # Admin dashboard data
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
        else:
            # Utilisateur classique
            context['my_qrcode_count'] = QRCode.objects.filter(user=request.user).count()
            context['last_qrcode'] = QRCode.objects.filter(user=request.user).order_by('-created_at').first()
            context['my_scans_today'] = Scan.objects.filter(qrcode__user=request.user, timestamp__date=today).count()

    return render(request, 'QRCode/index.html', context)


@login_required
def qr_code(request):
    """
    Handles QR code creation and listing for the logged-in user.
    - POST: creates a new QR code.
    - GET: lists all QR codes owned by the user.
    """
    if request.method == 'POST':
        url = request.POST.get('target_url')
        title = request.POST.get('title')

        if url and title and len(url)<=500 and len(title)<=150:
            #print("Generating QR Code...")
            qr_code_obj = QRCode.objects.create(
                user=request.user,
                title=title,
                target_url=url,
                is_active=True
            )
            # Build the URL for the QR code
            if DOMAIN_PROD :
                qr_code_url = f'{PROTOCOL_PROD}://{DOMAIN_PROD}/access/{qr_code_obj.uuid}'
            elif DOMAIN_NGROK :
                qr_code_url = f'{PROTOCOL_PROD}://{DOMAIN_NGROK}/access/{qr_code_obj.uuid}'
            else :
                qr_code_url = f'{PROTOCOL}://{DOMAIN}:{PORT}/access/{qr_code_obj.uuid}'

            # Generate QR code image
            img = qrcode_lib.make(qr_code_url)
            buffer = BytesIO()
            img.save(buffer, format="PNG")

            # Save ImageField
            filename = f"{qr_code_obj.uuid}.png"
            qr_code_obj.qr_image.save(filename, ContentFile(buffer.getvalue()), save=True)

            # Log creation action
            ActivityLog.objects.create(
                user=request.user,
                action_type='QR_CREATED',
                description=f"QR Code créé : {title}",
                url = qr_code_obj.target_url
            )
        return redirect('qr_code')

    # Les qr codes de l'utilisateur connecté (id) user_id

    # GET: List QR codes for the user
    qrcodes = QRCode.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'QRCode/qrcode.html' ,context={ 'qrcodes': qrcodes} )



@qr_owner_or_admin_required
@login_required
def qr_code_detail(request, qrcode):
    """
     Shows details and statistics for a single QR code.
     Allows updating the QR code on POST request.
     """
    if request.method == 'POST':
        url = request.POST.get('target_url')
        title = request.POST.get('title')
        is_active = request.POST.get('is_active') == 'on'

        if url and title and len(url)<=500 and len(title)<=150:
            qrcode.target_url = url
            qrcode.title = title
            qrcode.is_active = is_active
            qrcode.updated_at = now()

            # Rebuild QR code URL
            if DOMAIN_PROD :
                qr_code_url = f'{PROTOCOL_PROD}://{DOMAIN_PROD}/access/{qrcode.uuid}'
            elif DOMAIN_NGROK :
                qr_code_url = f'{PROTOCOL_PROD}://{DOMAIN_NGROK}/access/{qrcode.uuid}'
            else:
                qr_code_url = f'{PROTOCOL}://{DOMAIN}:{PORT}/access/{qrcode.uuid}'

            # Regenerate QR code image
            img = qrcode_lib.make(qr_code_url)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            filename = f"{qrcode.uuid}.png"
            qrcode.qr_image.save(filename, ContentFile(buffer.getvalue()), save=False)

            qrcode.save()

            # Log update action
            ActivityLog.objects.create(
                user=request.user,
                action_type='QR_UPDATED',
                description=f"QR Code mis à jour : {title}",
                url=qrcode.target_url
            )
            return redirect('qr_code_detail', uuid=qrcode.uuid)

    # Calculate stats for last 7 days scans
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

    # Calculate hourly scan stats
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

    chart_data = {
        "labels": labels,
        "data": data,
        "hour_labels": hour_labels,
        "hour_data": hour_data
    }
    return render(request, 'QRCode/detail.html', {
        'qrcode': qrcode,
        "chart_data": chart_data
    })


@qr_owner_or_admin_required
@login_required
def delete_qrcode(request,qrcode):
    """
    Deletes a QR code and its associated image files.
    Logs the deletion action.
    """

    delete_qrcode_file(qrcode)
    if qrcode:
        qrcode.delete()

        ActivityLog.objects.create(
            user=request.user,
            action_type='QR_DELETED',
            description=f"QR Code effacé : {qrcode.title}",
            url=qrcode.target_url
        )
        #print("QR Code deleted successfully.")

    return redirect('qr_code')

def delete_qrcode_file(qrcode):
    """
    Deletes files linked to a QRCode
    """
    # Directory where QR code images are stored
    qr_dir = os.path.join(MEDIA_ROOT, 'qrcodes') # adjust if stored elsewhere

    # Strict pattern: starts with the UUID, optionally followed by an underscore and some characters, then ends with .png
    pattern = re.compile(rf"^{re.escape(str(qrcode.uuid))}(_[^/\\]+)?\.png$")

    if os.path.exists(qr_dir):
        for filename in os.listdir(qr_dir):
            if pattern.match(filename):
                file_path = os.path.join(qr_dir, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

@qr_owner_or_admin_required
@login_required
def reload_qrcode_image(request, qrcode):
    """
    Regenerates the QR code image from the current target_url.
    Updates timestamp and saves the new image.
    """
    if qrcode.target_url:
        if DOMAIN_PROD:
            qr_code_url = f'{PROTOCOL_PROD}://{DOMAIN_PROD}/access/{qrcode.uuid}'
        elif DOMAIN_NGROK:
            qr_code_url = f'{PROTOCOL_PROD}://{DOMAIN_NGROK}/access/{qrcode.uuid}'
        else:
            qr_code_url = f'{PROTOCOL}://{DOMAIN}:{PORT}/access/{qrcode.uuid}'
        # Regenerate QR code image
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
    """
    AJAX endpoint for searching QR codes by uuid, title or url.
    Supports filtering by status (active/inactive/all).
    Returns JSON results.
    """
    query = request.GET.get('query', '').strip()
    search_type = request.GET.get('type', '').strip()
    status = request.GET.get('status', 'all').strip()

    if not query or not search_type:
        return JsonResponse([], safe=False)

    print()
    filters = Q()
    if search_type == "uuid":
        filters = Q(uuid__icontains=query)
    elif search_type == "title":
        filters = Q(title__icontains=query)
    elif search_type == "url":
        filters = Q(target_url__icontains=query)
    else:
        return JsonResponse([], safe=False)   # Invalid search type

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
            'is_active': qr.is_active,
        }
        for qr in qrcodes
    ]

    return JsonResponse(results, safe=False)
