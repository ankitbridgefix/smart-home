from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from django.db.models import Sum
from .models import Device, Telemetry
from .serializers import DeviceSerializer, TelemetrySerializer
from .permissions import IsOwner
import calendar
from datetime import date
from django.db.models.functions import TruncDay

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
        return Response({"device_id": device.id,"device_name":device.name ,"total_kwh": round(total, 4)})
    

    @action(detail=True, methods=["get"])
    def monthly_graph(self, request, pk=None):
        """
        Returns daily energy usage for a device in a given month.
        Accepts query param: ?month=January&year=2025 (year optional, defaults to current year)
        """
        device = self.get_object()
        month_name = request.query_params.get("month")
        year = int(request.query_params.get("year", date.today().year))

        if not month_name:
            return Response({"error": "Please provide a month (e.g., January, February)."}, status=400)

        try:
            month = list(calendar.month_name).index(month_name.capitalize())
            if month == 0:
                raise ValueError
        except ValueError:
            return Response({"error": f"Invalid month '{month_name}'."}, status=400)

        # Filter telemetry by year + month
        qs = device.telemetry.filter(timestamp__year=year, timestamp__month=month)

        # Group by day
        daily_data = (
            qs.annotate(day=TruncDay("timestamp"))
              .values("day")
              .annotate(total=Sum("energy_kwh"))
              .order_by("day")
        )

        return Response({
            "device_id": device.id,
            "device_name": device.name,
            "month": month_name.capitalize(),
            "year": year,
            "data": [
                {"date": entry["day"], "total_kwh": round(entry["total"], 4)}
                for entry in daily_data
            ]
        })