from rest_framework import serializers
from .models import Device, Telemetry

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ("id", "name", "slug")

class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = ("id", "device", "timestamp", "energy_kwh")
        read_only_fields = ("id",)
