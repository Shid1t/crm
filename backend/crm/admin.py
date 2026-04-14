from django.contrib import admin

from .models import ConfirmationTask, Customer, FileRecord, LogisticsRecord, MessageRecord, MessageThread, Order


admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(ConfirmationTask)
admin.site.register(FileRecord)
admin.site.register(LogisticsRecord)
admin.site.register(MessageThread)
admin.site.register(MessageRecord)

# Register your models here.
