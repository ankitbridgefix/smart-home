from django.contrib import admin
from .models import Telemetry, Device
# Register your models here.


class TelemetryAdmin(admin.ModelAdmin):
    list_display = ("device", "timestamp", "energy_kwh")
    list_filter = ("device", "timestamp")
    search_fields = ("device__name", "device__slug")



admin.site.register(Telemetry, TelemetryAdmin)