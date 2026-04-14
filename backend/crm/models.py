from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(TimeStampedModel):
    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default="enabled")
    remark = models.TextField(blank=True)

    def __str__(self):
        return self.company_name


class Order(TimeStampedModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("production", "Production"),
        ("shipped", "Shipped"),
        ("completed", "Completed"),
        ("exception", "Exception"),
    )

    order_no = models.CharField(max_length=64, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    order_date = models.DateField()
    currency = models.CharField(max_length=10, default="USD")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    eta = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.order_no


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    sku = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=200)
    spec = models.CharField(max_length=200, blank=True)
    qty = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total(self):
        return self.qty * self.unit_price


class ConfirmationTask(TimeStampedModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("revise", "Revise"),
        ("resubmitted", "Resubmitted"),
    )

    task_no = models.CharField(max_length=64, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="confirmation_tasks")
    item_type = models.CharField(max_length=50)
    item_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    latest_feedback = models.TextField(blank=True)


class FileRecord(TimeStampedModel):
    VISIBILITY_CHOICES = (
        ("customer", "Customer"),
        ("internal", "Internal"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="files")
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_path = models.CharField(max_length=500, blank=True)
    version = models.CharField(max_length=20, default="v1")
    size = models.CharField(max_length=30, blank=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="customer")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )


class LogisticsRecord(TimeStampedModel):
    STATUS_CHOICES = (
        ("preparing", "Preparing"),
        ("inTransit", "In Transit"),
        ("customs", "Customs"),
        ("delayed", "Delayed"),
        ("delivered", "Delivered"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="logistics")
    company = models.CharField(max_length=100)
    tracking_no = models.CharField(max_length=100)
    etd = models.DateField(null=True, blank=True)
    eta = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="preparing")
    latest_note = models.CharField(max_length=255, blank=True)


class MessageThread(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="message_threads")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="message_threads")
    title = models.CharField(max_length=200)


class MessageRecord(TimeStampedModel):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    sender_role = models.CharField(max_length=20, blank=True)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
