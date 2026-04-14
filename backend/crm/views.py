from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import ConfirmationTask, Customer, FileRecord, LogisticsRecord, MessageRecord, MessageThread, Order, OrderItem
from .permissions import IsAdminOrCustomerScoped
from .serializers import (
    ConfirmationTaskSerializer,
    CustomerSerializer,
    FileRecordSerializer,
    LogisticsRecordSerializer,
    MessageRecordSerializer,
    MessageThreadSerializer,
    OrderItemSerializer,
    OrderSerializer,
)


class CustomerScopedQuerysetMixin:
    customer_field = "customer"

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == "admin":
            return queryset
        if not user.customer_id:
            return queryset.none()
        lookup = {f"{self.customer_field}_id": user.customer_id}
        return queryset.filter(**lookup)


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all().order_by("-id")

    def get_queryset(self):
        queryset = Customer.objects.all().order_by("-id")
        user = self.request.user
        if user.role == "admin":
            return queryset
        if not user.customer_id:
            return queryset.none()
        return queryset.filter(id=user.customer_id)


class OrderViewSet(CustomerScopedQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("customer").filter(is_deleted=False).order_by("-id")

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order_no=order_no)
        return queryset

    def _ensure_admin_write(self):
        if self.request.user.role != "admin":
            raise PermissionDenied("Only admin can modify orders.")

    def create(self, request, *args, **kwargs):
        self._ensure_admin_write()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._ensure_admin_write()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._ensure_admin_write()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._ensure_admin_write()
        order = self.get_object()
        order.is_deleted = True
        order.deleted_at = timezone.now()
        order.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        return Response(status=204)


class OrderItemViewSet(CustomerScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.select_related("order", "order__customer").filter(order__is_deleted=False).order_by("id")
    customer_field = "order__customer"

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order__order_no=order_no)
        return queryset


class ConfirmationTaskViewSet(CustomerScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = ConfirmationTaskSerializer
    queryset = ConfirmationTask.objects.select_related("order", "order__customer").filter(order__is_deleted=False).order_by("-id")
    customer_field = "order__customer"

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order__order_no=order_no)
        return queryset


class FileRecordViewSet(CustomerScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = FileRecordSerializer
    queryset = FileRecord.objects.select_related("order", "order__customer", "uploaded_by").filter(order__is_deleted=False).order_by("-id")
    customer_field = "order__customer"

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order__order_no=order_no)
        return queryset


class LogisticsRecordViewSet(CustomerScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = LogisticsRecordSerializer
    queryset = LogisticsRecord.objects.select_related("order", "order__customer").filter(order__is_deleted=False).order_by("-id")
    customer_field = "order__customer"

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order__order_no=order_no)
        return queryset


class MessageThreadViewSet(CustomerScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = MessageThreadSerializer
    queryset = MessageThread.objects.select_related("customer", "order").filter(Q(order__is_deleted=False) | Q(order__isnull=True)).order_by("-id")

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order__order_no=order_no)
        return queryset


class MessageRecordViewSet(CustomerScopedQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = MessageRecordSerializer
    queryset = MessageRecord.objects.select_related("thread", "thread__customer", "sender").filter(Q(thread__order__is_deleted=False) | Q(thread__order__isnull=True)).order_by("created_at")
    customer_field = "thread__customer"
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = super().get_queryset()
        thread_id = self.request.query_params.get("thread")
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        return queryset

    def perform_create(self, serializer):
        thread_id = self.request.data.get("thread")
        if not thread_id:
            raise ValidationError({"thread": "This field is required."})

        try:
            thread = MessageThread.objects.select_related("customer").get(id=thread_id)
        except MessageThread.DoesNotExist as exc:
            raise ValidationError({"thread": "Thread does not exist."}) from exc

        user = self.request.user
        if user.role != "admin" and thread.customer_id != user.customer_id:
            raise PermissionDenied("No permission for this thread.")

        serializer.save(
            thread=thread,
            sender=user,
            sender_role=user.role,
            is_read=False,
        )
