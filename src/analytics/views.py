from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tracking.models import Scan
from QRCode.models import QRCode
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta

@login_required
def global_stats_view(request):
    user = request.user

    if user.is_superuser:
        scans = Scan.objects.all()
        qrcodes = QRCode.objects.all()
    else:
        qrcodes = QRCode.objects.filter(user=user)
        scans = Scan.objects.filter(qrcode__in=qrcodes)

    total_qrcodes = qrcodes.count()
    total_scans = scans.count()

    # Scans groupés par jour (7 derniers jours)
    last_7_days = now().date() - timedelta(days=6)
    scans_by_day = (
        scans.filter(timestamp__date__gte=last_7_days)
        .values('timestamp__date')
        .annotate(total=Count('id'))
        .order_by('timestamp__date')
    )

    return render(request, 'analytics/global_stats.html', {
        'total_qrcodes': total_qrcodes,
        'total_scans': total_scans,
        'scans_by_day': scans_by_day,
    })
