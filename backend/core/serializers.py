from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class PortalTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["customer_id"] = user.customer_id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "customer_id": user.customer_id,
            "display_name": user.get_full_name() or user.username,
        }
        return data


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    customer_id = serializers.IntegerField(read_only=True, allow_null=True)
    display_name = serializers.CharField(read_only=True)


class UserSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.company_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "customer", "customer_name", "is_enabled", "date_joined", "last_login"]
