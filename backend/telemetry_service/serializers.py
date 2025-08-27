from rest_framework import serializers
from .models import Device, Telemetry
from django.db.models import Sum
class DeviceSerializer(serializers.ModelSerializer):
    total_kwh = serializers.SerializerMethodField()
    class Meta:
        model = Device
        fields = ("id", "name", "slug", "total_kwh")
    
    def get_total_kwh(self, obj):
        # Aggregate total energy for the device
        return round(obj.telemetry.aggregate(total=Sum("energy_kwh"))["total"] or 0.0, 4)

class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = ("id", "device", "timestamp", "energy_kwh")
        read_only_fields = ("id",)
