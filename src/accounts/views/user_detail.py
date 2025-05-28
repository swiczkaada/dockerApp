from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

from QRCode.models import QRCode
from accounts.decorators import admin_or_superadmin_required
from accounts.models import CustomUser
from activityLog.models import ActivityLog
from tracking.models import Scan

@admin_or_superadmin_required
def user_detail_view(request, username):
    print(f"Accessing user detail for: {username}")

    user = get_object_or_404(CustomUser, username=username)
    qrcodes = QRCode.objects.filter(user=user).order_by('-created_at')
    last_qrcode = qrcodes.first() if qrcodes.exists() else None
    total_qrcodes = qrcodes.count()
    total_scans = Scan.objects.filter(qrcode__in=qrcodes).count()
    logs = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:20]

    context = {
        'user': user,
        'qrcodes': qrcodes,
        'last_qrcode': last_qrcode,
        'total_qrcodes': total_qrcodes,
        'total_scans': total_scans,
        'logs': logs,
    }
    return render(request, 'accounts/user_detail.html', context)


def view_403(request):
    """
    Custom 403 error view.
    """
    return render(request, 'accounts/403.html', status=403)