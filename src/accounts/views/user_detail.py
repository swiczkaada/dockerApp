from django.shortcuts import render, get_object_or_404

from QRCode.models import QRCode
from accounts.decorators import admin_or_superadmin_required
from accounts.models import CustomUser
from activityLog.models import ActivityLog
from tracking.models import Scan

@admin_or_superadmin_required
def user_detail_view(request, username):
    """
    Displays detailed information about a specific user.
    This view is restricted to admins or superadmins.

    Shows:
    - User's profile
    - List of their QR codes
    - Total number of QR codes and scans
    - Most recent QR code
    - Last 20 activity logs
    """
    # Retrieve the target user or show 404 if not found
    user = get_object_or_404(CustomUser, username=username)

    # Get all QR codes for the user, ordered by creation date (newest first)
    qrcodes = QRCode.objects.filter(user=user).order_by('-created_at')
    last_qrcode = qrcodes.first() if qrcodes.exists() else None

    # Compute total QR codes and scans associated with those codes
    total_qrcodes = qrcodes.count()
    total_scans = Scan.objects.filter(qrcode__in=qrcodes).count()

    # Fetch the last 20 activity logs for the user
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
    Custom handler for 403 - Forbidden errors.
    Rendered when a user tries to access a restricted area.
    """
    return render(request, 'accounts/403.html', status=403)