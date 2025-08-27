# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from rest_framework.test import APITestCase
# from telemetry_service.models import Device, Telemetry
# from django.utils import timezone
# from datetime import timedelta
# from rest_framework_simplejwt.tokens import RefreshToken

# User = get_user_model()

# class ChatQueryTests(APITestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username="u2", password="p2")
#         self.device = Device.objects.create(user=self.user, name="Fridge", slug="fridge")
#         now = timezone.now()
#         Telemetry.objects.create(device=self.device, timestamp=now - timedelta(hours=1), energy_kwh=0.1)
#         Telemetry.objects.create(device=self.device, timestamp=now - timedelta(minutes=30), energy_kwh=0.2)
#         self.url = reverse("chat_query")

#     def token(self):
#         return {"HTTP_AUTHORIZATION": f"Bearer {str(RefreshToken.for_user(self.user).access_token)}"}

#     def test_total_usage_intent(self):
#         res = self.client.post(self.url, {"question": "How much energy did my fridge use today?"}, format="json", **self.token())
#         self.assertEqual(res.status_code, 200)
#         self.assertIn("summary", res.data)
#         self.assertIn("series", res.data)

#     def test_top_devices_intent(self):
#         res = self.client.post(self.url, {"question": "Which of my devices are using the most power today?"}, format="json", **self.token())
#         # self.assertEqual(res.status_code, 200)
#         self.assertIn("devices", res.data)



# chat_service/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .nlp import detect_intent, extract_entities
# from .models import DeviceUsage
from django.utils.timezone import now, timedelta

class ChatQueryView(APIView):
    def post(self, request):
        question = request.data.get("question", "")
        intent = detect_intent(question)
        entities = extract_entities(question)

        # Default date filter
        date = entities.get("date", "today")
        today = now().date()
        if date == "yesterday":
            target_date = today - timedelta(days=1)
        else:
            target_date = today

        # --- Intent handling ---
        if intent == "energy_usage":
            device = entities.get("device")
            if not device:
                return Response(
                    {"error": "Please specify a device (e.g., 'my fridge', 'my AC')."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # usage = DeviceUsage.objects.filter(device__icontains=device, date=target_date).first()
            # if usage:
                # return Response({"device": device, "date": str(target_date), "usage": usage.usage_kwh})
            return Response({"device": device, "date": str(target_date), "usage": 0})

        elif intent == "top_devices":
            # ✅ Do NOT require device here
            # usages = DeviceUsage.objects.filter(date=target_date).order_by("-usage_kwh")[:5]
            devices = [{"device": u.device, "usage": u.usage_kwh} for u in usages]
            return Response({"date": str(target_date), "devices": devices})

        else:
            return Response({"error": "Sorry, I didn’t understand that."}, status=status.HTTP_400_BAD_REQUEST)
