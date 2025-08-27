
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Device, Telemetry
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def auth_header(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

class TelemetryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="p1")
        self.device = Device.objects.create(user=self.user, name="Fridge", slug="fridge")

    def test_create_telemetry_and_summary(self):
        url = reverse("device-telemetry", args=[self.device.id])
        now = timezone.now()
        payload = {"timestamp": now.isoformat(), "energy_kwh": 0.02}
        res = self.client.post(url, payload, format="json", **auth_header(self.user))
        self.assertEqual(res.status_code, 201)

        sum_url = reverse("device-summary", args=[self.device.id])
        res2 = self.client.get(sum_url, **auth_header(self.user))
        self.assertEqual(res2.status_code, 200)
        self.assertIn("total_kwh", res2.data)
