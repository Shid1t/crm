import os
import uuid

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
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


class AdminWriteMixin:
    def ensure_admin_write(self):
        if self.request.user.role != "admin":
            raise PermissionDenied("Only admin can modify data.")


def ensure_order_writable(order):
    if order.is_deleted:
        raise ValidationError({"order": "Order has been deleted."})


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


class OrderViewSet(AdminWriteMixin, CustomerScopedQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("customer").filter(is_deleted=False).order_by("-id")

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order_no=order_no)
        return queryset

    def create(self, request, *args, **kwargs):
        self.ensure_admin_write()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.ensure_admin_write()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.ensure_admin_write()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.ensure_admin_write()
        order = self.get_object()
        order.is_deleted = True
        order.deleted_at = timezone.now()
        order.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        return Response(status=204)


class OrderItemViewSet(AdminWriteMixin, CustomerScopedQuerysetMixin, viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data["order"]
        ensure_order_writable(order)
        serializer.save()

    def perform_update(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data.get("order", serializer.instance.order)
        ensure_order_writable(order)
        serializer.save()

    def perform_destroy(self, instance):
        self.ensure_admin_write()
        instance.delete()


class ConfirmationTaskViewSet(AdminWriteMixin, CustomerScopedQuerysetMixin, viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data["order"]
        ensure_order_writable(order)
        if not serializer.validated_data.get("task_no"):
            stamp = timezone.now().strftime("%y%m%d%H%M%S")
            serializer.save(task_no=f"CF-{stamp}-{uuid.uuid4().hex[:4].upper()}")
            return
        serializer.save()

    def perform_update(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data.get("order", serializer.instance.order)
        ensure_order_writable(order)
        serializer.save()

    def perform_destroy(self, instance):
        self.ensure_admin_write()
        instance.delete()


class FileRecordViewSet(AdminWriteMixin, CustomerScopedQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = FileRecordSerializer
    queryset = FileRecord.objects.select_related("order", "order__customer", "uploaded_by").filter(order__is_deleted=False).order_by("-id")
    customer_field = "order__customer"
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order__order_no=order_no)
        return queryset

    def perform_create(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data["order"]
        ensure_order_writable(order)

        uploaded = self.request.FILES.get("file")
        if not uploaded:
            raise ValidationError({"file": "This field is required."})

        ext = os.path.splitext(uploaded.name)[1]
        safe_name = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
        relative_dir = os.path.join("orders", order.order_no)
        absolute_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
        os.makedirs(absolute_dir, exist_ok=True)
        absolute_path = os.path.join(absolute_dir, safe_name)

        with open(absolute_path, "wb+") as destination:
            for chunk in uploaded.chunks():
                destination.write(chunk)

        relative_path = os.path.join(relative_dir, safe_name)
        serializer.save(
            file_name=uploaded.name,
            file_path=relative_path,
            size=f"{uploaded.size / 1024:.1f} KB",
            uploaded_by=self.request.user,
        )

    def perform_update(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data.get("order", serializer.instance.order)
        ensure_order_writable(order)

        uploaded = self.request.FILES.get("file")
        if uploaded:
            old_path = serializer.instance.file_path
            if old_path and not old_path.startswith("/"):
                old_abs = os.path.join(settings.MEDIA_ROOT, old_path)
                if os.path.exists(old_abs):
                    os.remove(old_abs)

            ext = os.path.splitext(uploaded.name)[1]
            safe_name = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
            relative_dir = os.path.join("orders", order.order_no)
            absolute_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
            os.makedirs(absolute_dir, exist_ok=True)
            absolute_path = os.path.join(absolute_dir, safe_name)
            with open(absolute_path, "wb+") as destination:
                for chunk in uploaded.chunks():
                    destination.write(chunk)

            serializer.save(
                file_name=uploaded.name,
                file_path=os.path.join(relative_dir, safe_name),
                size=f"{uploaded.size / 1024:.1f} KB",
                uploaded_by=self.request.user,
            )
            return

        serializer.save()

    def perform_destroy(self, instance):
        self.ensure_admin_write()
        file_path = instance.file_path
        instance.delete()
        if file_path and not file_path.startswith("/"):
            absolute = os.path.join(settings.MEDIA_ROOT, file_path)
            if os.path.exists(absolute):
                os.remove(absolute)


class LogisticsRecordViewSet(AdminWriteMixin, CustomerScopedQuerysetMixin, viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data["order"]
        ensure_order_writable(order)
        serializer.save()

    def perform_update(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data.get("order", serializer.instance.order)
        ensure_order_writable(order)
        serializer.save()

    def perform_destroy(self, instance):
        self.ensure_admin_write()
        instance.delete()


class MessageThreadViewSet(AdminWriteMixin, CustomerScopedQuerysetMixin, viewsets.ModelViewSet):
    permission_classes = [IsAdminOrCustomerScoped]
    serializer_class = MessageThreadSerializer
    queryset = MessageThread.objects.select_related("customer", "order").filter(Q(order__is_deleted=False) | Q(order__isnull=True)).order_by("-id")
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = super().get_queryset()
        order_no = self.request.query_params.get("order_no")
        if order_no:
            queryset = queryset.filter(order__order_no=order_no)
        return queryset

    def perform_create(self, serializer):
        self.ensure_admin_write()
        order = serializer.validated_data.get("order")
        customer = serializer.validated_data.get("customer")
        if order:
            ensure_order_writable(order)
            if customer and customer.id != order.customer_id:
                raise ValidationError({"customer": "Customer does not match order."})
            serializer.save(customer=order.customer)
            return
        serializer.save()


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
        parent_id = self.request.data.get("parent")

        try:
            thread = MessageThread.objects.select_related("customer").get(id=thread_id)
        except MessageThread.DoesNotExist as exc:
            raise ValidationError({"thread": "Thread does not exist."}) from exc

        user = self.request.user
        if user.role != "admin" and thread.customer_id != user.customer_id:
            raise PermissionDenied("No permission for this thread.")

        parent = None
        if parent_id:
            try:
                parent = MessageRecord.objects.get(id=parent_id, thread_id=thread.id)
            except MessageRecord.DoesNotExist as exc:
                raise ValidationError({"parent": "Parent message does not exist in this thread."}) from exc

        serializer.save(
            thread=thread,
            parent=parent,
            sender=user,
            sender_role=user.role,
            is_read=False,
        )
