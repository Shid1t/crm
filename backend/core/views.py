from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import CurrentUserSerializer, PortalTokenObtainPairSerializer, UserSerializer


class PortalTokenObtainPairView(TokenObtainPairView):
    serializer_class = PortalTokenObtainPairSerializer


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payload = {
            "id": request.user.id,
            "username": request.user.username,
            "role": request.user.role,
            "customer_id": request.user.customer_id,
            "display_name": request.user.get_full_name() or request.user.username,
        }
        serializer = CurrentUserSerializer(payload)
        return Response(serializer.data)


class IsAdminUser:
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == "admin"


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.select_related("customer").all().order_by("-id")
