from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum
from django.utils.dateparse import parse_datetime
from telemetry_service.models import Device, Telemetry
from .nlp import parse_query

def _parse_bounds(req):
    start = req.query_params.get("start")
    end = req.query_params.get("end")
    return parse_datetime(start) if start else None, parse_datetime(end) if end else None

class QueryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Accepts: { "question": "How much energy did my fridge use yesterday?" }
        Optionally supports query params: ?start=&end= (ISO)
        """
        q = request.data.get("question", "")
        if not q:
            return Response({"error": "Missing 'question'."}, status=400)

        parsed = parse_query(q)
        qs_start, qs_end = _parse_bounds(request)
        if qs_start or qs_end:
            parsed["start"] = qs_start or parsed["start"]
            parsed["end"] = qs_end or parsed["end"]

        intent = parsed["intent"]
        start, end = parsed["start"], parsed["end"]
        device_slug = parsed["device_slug"]

        if intent == "total_usage":
            if not device_slug:
                return Response({"error": "Please specify a device (e.g., 'my fridge', 'my AC')."}, status=400)
            try:
                device = Device.objects.get(user=request.user, slug=device_slug)
            except Device.DoesNotExist:
                return Response({"error": f"Device '{device_slug}' not found for user."}, status=404)

            telemetry = Telemetry.objects.filter(device=device)
            if start:
                telemetry = telemetry.filter(timestamp__gte=start)
            if end:
                telemetry = telemetry.filter(timestamp__lte=end)

            total = telemetry.aggregate(total=Sum("energy_kwh"))["total"] or 0.0

            # small time-series (hourly) for frontend chart
            # Postgres-friendly: truncate to hour (fallback in Python if needed)
            from django.db.models.functions import TruncHour
            series = (
                telemetry.annotate(h=TruncHour("timestamp"))
                .values("h").order_by("h")
                .annotate(kwh=Sum("energy_kwh"))
            )
            data = [{"timestamp": s["h"], "kwh": float(s["kwh"])} for s in series]

            return Response({
                "intent": intent,
                "device": {"id": device.id, "name": device.name, "slug": device.slug},
                "window": {"start": start, "end": end},
                "summary": {"total_kwh": round(total, 4)},
                "series": data,
            })

        # top_devices intent
        telemetry = Telemetry.objects.filter(device__user=request.user)
        if start:
            telemetry = telemetry.filter(timestamp__gte=start)
        if end:
            telemetry = telemetry.filter(timestamp__lte=end)

        rows = (telemetry
                .values("device__id", "device__name", "device__slug")
                .annotate(total_kwh=Sum("energy_kwh"))
                .order_by("-total_kwh")[:5])

        return Response({
            "intent": "top_devices",
            "window": {"start": start, "end": end},
            "devices": [
                {"id": r["device__id"], "name": r["device__name"], "slug": r["device__slug"], "total_kwh": round(float(r["total_kwh"] or 0.0), 4)}
                for r in rows
            ],
        }, status=status.HTTP_200_OK)
