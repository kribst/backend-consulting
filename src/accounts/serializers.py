from rest_framework import serializers

from .models import AdminUser


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ("id", "nom", "email", "role")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
