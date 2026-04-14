from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ConfirmationTaskViewSet,
    CustomerViewSet,
    FileRecordViewSet,
    LogisticsRecordViewSet,
    MessageRecordViewSet,
    MessageThreadViewSet,
    OrderItemViewSet,
    OrderViewSet,
)

router = DefaultRouter()
router.register("customers", CustomerViewSet, basename="customers")
router.register("orders", OrderViewSet, basename="orders")
router.register("order-items", OrderItemViewSet, basename="order-items")
router.register("confirmations", ConfirmationTaskViewSet, basename="confirmations")
router.register("files", FileRecordViewSet, basename="files")
router.register("logistics", LogisticsRecordViewSet, basename="logistics")
router.register("messages", MessageThreadViewSet, basename="messages")
router.register("message-records", MessageRecordViewSet, basename="message-records")

urlpatterns = [
    path("", include(router.urls)),
]
