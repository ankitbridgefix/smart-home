from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from telemetry_service.models import Device, Telemetry

User = get_user_model()

DEVICES = [
    ("fridge", "Fridge"),
    ("ac", "AC"),
    ("tv", "TV"),
    ("washer", "Washing Machine"),
    ("router", "Router"),
]

class Command(BaseCommand):
    help = "Generate 24 hours of 1-min interval telemetry for 5 devices"

    def add_arguments(self, parser):
        parser.add_argument("--username", default="ankit", help="User to attach devices/telemetry to")

    def handle(self, *args, **opts):
        username = opts["username"]
        user, _ = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
        user.set_password("Pass@123")
        user.save()

        # Create devices if missing
        devices = []
        for slug, name in DEVICES:
            d, _ = Device.objects.get_or_create(user=user, slug=slug, defaults={"name": name})
            devices.append(d)

        # Generate last 24 hours (UTC)
        end = timezone.now().replace(second=0, microsecond=0)
        start = end - timedelta(hours=24)

        # Delete overlapping telemetry for clean demo
        Telemetry.objects.filter(device__in=devices, timestamp__gte=start, timestamp__lte=end).delete()

        # per-minute rows
        cur = start
        rows = []
        while cur < end:
            for d in devices:
                # simple profiles
                base = {
                    "fridge": 0.012,   # ~0.72 kWh/day
                    "ac": 0.2 if 10 <= cur.hour <= 22 else 0.05,  # higher during day
                    "tv": 0.05 if 18 <= cur.hour <= 23 else 0.01,
                    "washer": 0.5 if (cur.hour == 8 and cur.minute < 45) else 0.0,
                    "router": 0.005,
                }.get(d.slug, 0.01)
                jitter = random.uniform(-0.003, 0.003)
                kwh = max(base + jitter, 0.0)
                rows.append(Telemetry(device=d, timestamp=cur, energy_kwh=round(kwh, 5)))
            cur += timedelta(minutes=1)

            # bulk insert in chunks to save memory
            if len(rows) >= 5000:
                Telemetry.objects.bulk_create(rows, ignore_conflicts=True)
                rows = []

        if rows:
            Telemetry.objects.bulk_create(rows, ignore_conflicts=True) 

        self.stdout.write(self.style.SUCCESS("Generated telemetry for last 24 hours."))
        self.stdout.write(self.style.SUCCESS("Login with username='ankit', password='Pass@123'"))
