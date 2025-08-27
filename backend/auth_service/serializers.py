from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)
    role = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Role.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "role")

    def create(self, validated_data):
        role = validated_data.pop("role", None)
        user = User.objects.create_user(**validated_data)
        if role:
            user.role = role
            user.save()
        return user


class MeSerializer(serializers.ModelSerializer):
    """Serializer for current logged-in user profile"""
    role = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "role")
