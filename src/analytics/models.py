from django.db import models
from django.conf import settings

from dockerApp.settings import AUTH_USER_MODEL


class QRCodeStatistic(models.Model):
    qrcode = models.ForeignKey('QRCode.QRCode', on_delete=models.CASCADE, related_name='statistics')
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    scan_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('qrcode', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.qrcode.title} - {self.date} : {self.scan_count} scans"
