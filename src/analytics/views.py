from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tracking.models import Scan
from QRCode.models import QRCode
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta
from django.db.models.functions import TruncDay, TruncMonth, ExtractHour
import json

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

    # --------- Scans par jour sur 30 jours ---------
    last_30_days = now().date() - timedelta(days=29)
    scans_30_days_qs = (
        scans.filter(timestamp__date__gte=last_30_days)
        .annotate(day=TruncDay('timestamp'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )
    scans_30_days_dict = {entry['day'].date().isoformat(): entry['total'] for entry in scans_30_days_qs}

    labels_30_days = []
    data_30_days = []
    for i in range(30):
        day = (last_30_days + timedelta(days=i)).isoformat()
        labels_30_days.append(day)
        data_30_days.append(scans_30_days_dict.get(day, 0))

    # --------- Scans par mois sur 6 derniers mois ---------
    last_6_months_date = now().date().replace(day=1) - timedelta(days=180)  # approx 6 mois avant
    scans_6_months_qs = (
        scans.filter(timestamp__date__gte=last_6_months_date)
        .annotate(month=TruncMonth('timestamp'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    scans_6_months_dict = {entry['month'].date().strftime('%Y-%m'): entry['total'] for entry in scans_6_months_qs}

    # Générer labels mois en format YYYY-MM sur 6 mois
    from dateutil.relativedelta import relativedelta
    labels_6_months = []
    data_6_months = []
    current_month = now().date().replace(day=1) - relativedelta(months=5)
    for _ in range(6):
        label = current_month.strftime('%Y-%m')
        labels_6_months.append(label)
        data_6_months.append(scans_6_months_dict.get(label, 0))
        current_month += relativedelta(months=1)

    # --------- Top 5 QR codes les plus scannés ---------
    top_qrcodes_qs = (
        qrcodes.annotate(scan_count=Count('scans'))
        .order_by('-scan_count')[:5]
        .values('title', 'scan_count')
    )
    top_qrcodes_labels = [entry['title'] for entry in top_qrcodes_qs]
    top_qrcodes_data = [entry['scan_count'] for entry in top_qrcodes_qs]

    # --------- Moyenne quotidienne des scans sur la période de 30 jours ---------
    days_observed = 30
    avg_daily_scans = sum(data_30_days) / days_observed if days_observed > 0 else 0

    # --------- Distribution par heure de la journée (0-23h) ---------
    scans_by_hour_qs = (
        scans
        .annotate(hour=ExtractHour('timestamp'))
        .values('hour')
        .annotate(total=Count('id'))
        .order_by('hour')
    )
    scans_by_hour_dict = {entry['hour']: entry['total'] for entry in scans_by_hour_qs}
    hours_labels = list(range(24))
    scans_by_hour_data = [scans_by_hour_dict.get(h, 0) for h in hours_labels]

    # --------- QR codes actifs vs inactifs ---------
    active_count = qrcodes.filter(is_active=True).count()
    inactive_count = qrcodes.filter(is_active=False).count()

    return render(request, 'analytics/global_stats.html', {
        'total_qrcodes': total_qrcodes,
        'total_scans': total_scans,

        'labels_30_days': json.dumps(labels_30_days),
        'data_30_days': json.dumps(data_30_days),

        'labels_6_months': json.dumps(labels_6_months),
        'data_6_months': json.dumps(data_6_months),

        'top_qrcodes_labels': json.dumps(top_qrcodes_labels),
        'top_qrcodes_data': json.dumps(top_qrcodes_data),

        'avg_daily_scans': avg_daily_scans,

        'hours_labels': json.dumps(hours_labels),
        'scans_by_hour_data': json.dumps(scans_by_hour_data),

        'active_count': active_count,
        'inactive_count': inactive_count,
    })
