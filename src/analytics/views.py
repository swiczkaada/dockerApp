import json

from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth, ExtractHour
from django.shortcuts import render
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

from tracking.models import Scan
from QRCode.models import QRCode


@login_required
def global_stats_view(request):
    """
    Renders a global dashboard view with analytics data for QR code scans.
    Superusers see all data, regular users see only their own.
    """
    user = request.user

    # Fetch QR codes and scans based on user permissions
    if user.is_superuser:
        scans = Scan.objects.all()
        qrcodes = QRCode.objects.all()
    else:
        qrcodes = QRCode.objects.filter(user=user)
        scans = Scan.objects.filter(qrcode__in=qrcodes)

    total_qrcodes = qrcodes.count()
    total_scans = scans.count()

    # === [1] Scans per day (last 30 days) ===
    days_range = 30
    last_30_days = now().date() - timedelta(days=days_range - 1)
    daily_scans_qs = (
        scans.filter(timestamp__date__gte=last_30_days)
        .annotate(day=TruncDay('timestamp'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )
    # Map results to dictionary {YYYY-MM-DD: count}
    scans_by_day = {entry['day'].date().isoformat(): entry['total'] for entry in daily_scans_qs}

    labels_30_days = []
    data_30_days = []
    for i in range(days_range):
        day = (last_30_days + timedelta(days=i)).isoformat()
        labels_30_days.append(day)
        data_30_days.append(scans_by_day.get(day, 0))

    # === [2] Scans per month (last 6 months) ===
    months_range = 6
    start_month = now().date().replace(day=1) - relativedelta(months=months_range - 1)
    monthly_scans_qs = (
        scans.filter(timestamp__date__gte=start_month)
        .annotate(month=TruncMonth('timestamp'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    scans_by_month = {entry['month'].date().strftime('%Y-%m'): entry['total'] for entry in monthly_scans_qs}

    # Generate month labels in YYYY-MM format over 6 months
    labels_6_months = []
    data_6_months = []
    current_month = start_month
    for _ in range(months_range):
        label = current_month.strftime('%Y-%m')
        labels_6_months.append(label)
        data_6_months.append(scans_by_month.get(label, 0))
        current_month += relativedelta(months=1)

    # === [3] Top 5 most scanned QR codes ===
    top_qrcodes_qs = (
        qrcodes.annotate(scan_count=Count('scans'))
        .order_by('-scan_count')[:5]
        .values('title', 'scan_count')
    )
    top_qrcodes_labels = [entry['title'][:10] for entry in top_qrcodes_qs]
    top_qrcodes_data = [entry['scan_count'] for entry in top_qrcodes_qs]

    # === [4] Daily average over the last 30 days ===
    days_observed = 30
    avg_daily_scans = sum(data_30_days) / days_observed if days_observed > 0 else 0

    # === [5] Scan distribution by hour of the day (0–23) ===
    hourly_scans_qs = (
        scans
        .annotate(hour=ExtractHour('timestamp'))
        .values('hour')
        .annotate(total=Count('id'))
        .order_by('hour')
    )
    scans_by_hour = {entry['hour']: entry['total'] for entry in hourly_scans_qs}
    hours_labels = list(range(24))
    scans_by_hour_data = [scans_by_hour.get(h, 0) for h in hours_labels]

    # === [6] Active vs inactive QR codes ===
    active_count = qrcodes.filter(is_active=True).count()
    inactive_count = qrcodes.filter(is_active=False).count()

    # === [7] Top 5 most scanned cities ===
    top_cities_qs = (
        scans
        .filter(geo_city__isnull=False)
        .exclude(geo_city='')
        .values('geo_city')
        .annotate(scan_count=Count('id'))
        .order_by('-scan_count')[:5]
    )

    top_cities_labels = [entry['geo_city'] for entry in top_cities_qs]
    top_cities_data = [entry['scan_count'] for entry in top_cities_qs]

    # === [8] Scans by zone Île-de-France ===
    idf_scans_qs = (
        scans
        .filter(geo_region__isnull=False)
        .exclude(geo_region='')
        .filter(geo_region__icontains="Île-de-France")
        .filter(geo_city__isnull=False)
        .exclude(geo_city='')
        .values('geo_city')
        .annotate(scan_count=Count('id'))
    )

    idf_city_scans = {}
    for entry in idf_scans_qs:
        city = entry['geo_city'] or 'Inconnu'
        idf_city_scans[city] = idf_city_scans.get(city, 0) + entry['scan_count']

    idf_cities_labels = list(idf_city_scans.keys())
    idf_scans_data = list(idf_city_scans.values())

    # === [9] Scans by region France ===
    france_region_scans_qs = (
        scans
        .filter(geo_region__isnull=False)
        .exclude(geo_region='')
        .values('geo_region')
        .annotate(scan_count=Count('id'))
        .order_by('-scan_count')
    )

    france_regions_labels = [entry['geo_region'] for entry in france_region_scans_qs]
    france_regions_data = [entry['scan_count'] for entry in france_region_scans_qs]

    # === [10] GeoJSON data for heat maps (France only) ===
    heatmap_points = []
    for scan in scans:
        if scan.geo_latitude and scan.geo_longitude:
            try:
                lat = float(scan.geo_latitude)
                lng = float(scan.geo_longitude)

                if scan.geo_country and scan.geo_country.lower() != 'france':
                    continue

                heatmap_points.append([lat, lng])
            except (TypeError, ValueError):
                continue

    chart_data = {
        "labels30Days": labels_30_days,
        "data30Days": data_30_days,

        'labels6Months': labels_6_months,
        'data6Months': data_6_months,

        'topQRCodesLabels': top_qrcodes_labels,
        'topQRCodesData': top_qrcodes_data,

        'hoursLabels': hours_labels,
        'scansByHourData': scans_by_hour_data,

        'activeCount': active_count,
        'inactiveCount': inactive_count,

        'topCitiesLabels': top_cities_labels,
        'topCitiesData': top_cities_data,

        'idfCitiesLabels': idf_cities_labels,
        'idfCitiesData': idf_scans_data,

        'franceRegionsLabels': france_regions_labels,
        'franceRegionsData': france_regions_data,

        'heatmapPoints':heatmap_points,
    }
    return render(request, 'analytics/global_stats.html', {
        "chart_data": chart_data,
        "total_qrcodes": total_qrcodes,
        "total_scans": total_scans,
        "avg_daily_scans": avg_daily_scans,
    })



