from django.db import models
from django.urls import reverse

from dockerApp.settings import AUTH_USER_MODEL

import uuid


class QRCode(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    target_url = models.URLField(max_length=500)
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

    def get_absolute_url(self):
        return reverse("qr_code_detail", kwargs={"uuid": self.uuid})

    @property
    def scan_count(self):
        return self.scans.count()
