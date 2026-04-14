from rest_framework import serializers

from .models import ConfirmationTask, Customer, FileRecord, LogisticsRecord, MessageRecord, MessageThread, Order, OrderItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.company_name", read_only=True)

    class Meta:
        model = Order
        fields = "__all__"

    def validate(self, attrs):
        order_date = attrs.get("order_date")
        eta = attrs.get("eta")
        amount = attrs.get("amount")

        if self.instance:
            if order_date is None:
                order_date = self.instance.order_date
            if eta is None:
                eta = self.instance.eta
            if amount is None:
                amount = self.instance.amount

        if eta and order_date and eta < order_date:
            raise serializers.ValidationError({"eta": "ETA must be on or after order date."})

        if amount is not None and amount < 0:
            raise serializers.ValidationError({"amount": "Amount must be non-negative."})

        return attrs


class ConfirmationTaskSerializer(serializers.ModelSerializer):
    order_no = serializers.CharField(source="order.order_no", read_only=True)

    class Meta:
        model = ConfirmationTask
        fields = "__all__"


class FileRecordSerializer(serializers.ModelSerializer):
    order_no = serializers.CharField(source="order.order_no", read_only=True)
    uploader_name = serializers.SerializerMethodField()

    class Meta:
        model = FileRecord
        fields = "__all__"

    def get_uploader_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.username
        return None


class LogisticsRecordSerializer(serializers.ModelSerializer):
    order_no = serializers.CharField(source="order.order_no", read_only=True)

    class Meta:
        model = LogisticsRecord
        fields = "__all__"


class MessageThreadSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.company_name", read_only=True)
    order_no = serializers.CharField(source="order.order_no", read_only=True)

    class Meta:
        model = MessageThread
        fields = "__all__"


class MessageRecordSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = MessageRecord
        fields = "__all__"
