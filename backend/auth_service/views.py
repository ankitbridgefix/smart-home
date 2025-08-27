from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, MeSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Choose serializer dynamically"""
        if self.action == "me":
            return MeSerializer
        if self.action == "create":
            return RegisterSerializer
        return MeSerializer   # default for other actions

    def get_permissions(self):
        """Allow registration without authentication"""
        if self.action == "create":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """User registration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current logged-in user"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
