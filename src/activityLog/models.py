# models.py
from datetime import timedelta

from django.db import models
from django.utils.timezone import now

from dockerApp.settings import AUTH_USER_MODEL

class ActivityLog(models.Model):
    ACTION_TYPES = [
    ('QR_CREATED', 'QR Code crée'),
    ('QR_UPDATED', 'QR Code mis à jour'),
    ('QR_DELETED', 'QR Code effacé'),
    ('PERMISSION_CHANGED', 'Permission changée'),
    ('USER_DEACTIVATED', 'User désactivé'),
    ('USER_REACTIVATED', 'User réactivé'),
    ('USER_UPDATED', 'User mis à jour'),
    ('USER_CREATED', 'User créé'),
    ('USER_DELETED', 'User supprimé'),
    ]


    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=150, choices=ACTION_TYPES)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action_type} @ {self.timestamp}"

    def save(self, *args, **kwargs):
        self.try_cleanup_logs()
        super().save(*args, **kwargs)

    @classmethod
    def try_cleanup_logs(cls):
        tracker, _ = LogCleanupTracker.objects.get_or_create(id=1)
        if now() - tracker.last_cleanup > timedelta(days=1):
            cls.cleanup_old_logs()
            tracker.last_cleanup = now()
            tracker.save()

    @staticmethod
    def cleanup_old_logs():
        cutoff_date = now() - timedelta(days=10)
        deleted_count, _ = ActivityLog.objects.filter(timestamp__lt=cutoff_date).delete()
        print(f"{deleted_count} logs supprimés (plus de 10 jours)")


class LogCleanupTracker(models.Model):
    last_cleanup = models.DateTimeField(default=now)

    def __str__(self):
        return f"Dernier nettoyage: {self.last_cleanup}"