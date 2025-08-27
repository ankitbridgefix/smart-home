from django.db import models
from django.conf import settings

class Device(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)

    class Meta:
        unique_together = ("user", "slug")

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Telemetry(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="telemetry")
    timestamp = models.DateTimeField(db_index=True)
    energy_kwh = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=["device", "timestamp"]),
        ]
        ordering = ["-timestamp"]
