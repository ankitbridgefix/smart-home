from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.db.models import Sum
from .models import Device, Telemetry
from .serializers import DeviceSerializer, TelemetrySerializer
from .permissions import IsOwner

class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Device.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get", "post"])
    def telemetry(self, request, pk=None):
        device = self.get_object()
        if request.method == "POST":
            data = request.data.copy()
            data["device"] = device.id
            ser = TelemetrySerializer(data=data)
            ser.is_valid(raise_exception=True)
            ser.save()
            return Response(ser.data, status=201)

        # GET — optional filters ?start=ISO&end=ISO
        qs = device.telemetry.all()
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if start:
            qs = qs.filter(timestamp__gte=parse_datetime(start))
        if end:
            qs = qs.filter(timestamp__lte=parse_datetime(end))
        return Response(TelemetrySerializer(qs[:1000], many=True).data)

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        device = self.get_object()
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        qs = device.telemetry.all()
        if start:
            qs = qs.filter(timestamp__gte=parse_datetime(start))
        if end:
            qs = qs.filter(timestamp__lte=parse_datetime(end))
        total = qs.aggregate(total=Sum("energy_kwh"))["total"] or 0.0
        return Response({"device_id": device.id, "total_kwh": round(total, 4)})
