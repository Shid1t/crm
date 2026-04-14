import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models import User
from crm.models import (
    ConfirmationTask, Customer, FileRecord, LogisticsRecord,
    MessageRecord, MessageThread, Order, OrderItem,
)

PRODUCTS = [
    ("Impact Wrench", "20V Cordless Impact Wrench with 2 Batteries"),
    ("Cordless Drill", "18V Compact Cordless Drill/Driver Kit"),
    ("Angle Grinder", "4.5-Inch 11-Amp Corded Angle Grinder"),
    ("Circular Saw", "7.25-Inch 15-Amp Corded Circular Saw"),
    ("Rotary Hammer", "SDS-Plus 1-1/8-Inch Rotary Hammer"),
    ("Heat Gun", "2000W Dual-Temperature Heat Gun"),
    ("Planer", "3-1/4-Inch Electric Hand Planer"),
    ("Jigsaw", "6-Amp Orbital Action Jigsaw"),
    ("Reciprocating Saw", "12-Amp Corded Reciprocating Saw"),
    ("Belt Sander", "3-Inch x 21-Inch Corded Belt Sander"),
    ("Orbital Sander", "5-Inch Random Orbital Sander"),
    ("Demolition Hammer", "35-Joule Electric Demolition Hammer"),
    ("Tile Cutter", "24-Inch Manual Tile Cutter"),
    ("Table Saw", "10-Inch 15-Amp Portable Table Saw"),
    ("Miter Saw", "10-Inch 15-Amp Sliding Compound Miter Saw"),
    ("Band Saw", "9-Inch 2.5-Amp Desktop Band Saw"),
    ("Core Drill", "4-Inch 1500W Core Drill Machine"),
    ("Mag Drill", "1-3/16-Inch Magnetic Base Drilling Machine"),
    ("Bench Grinder", "8-Inch 5.5-Amp Bench Grinder"),
    ("Pedestal Grinder", "10-Inch 3/4 HP Pedestal Grinder"),
    ("Winch", "2500-LB Electric Winch with Remote"),
    ("Lifting Hoist", "1000KG Electric Chain Hoist"),
    ("Hydraulic Jack", "3-Ton Hydraulic Floor Jack"),
    ("Hydraulic Press", "12V 10-Ton Hydraulic Press"),
    ("Pipe Threader", "1/2-2-Inch Portable Pipe Threader"),
    ("Pipe Cutter", "2-Inch Super-Type Pipe Cutter"),
    ("Metal Shear", "4.3-Amp 14-Gauge Metal Shear"),
    ("Nibbler", "3/16-Inch Sheet Metal Nibbler"),
    ("Electric Hoist", "220V 1-Ton Electric Wire Rope Hoist"),
    ("Surface Grinder", "6-Inch Precision Surface Grinder"),
    ("Milling Machine", "2-Speed Variable Mill/Drill Machine"),
    ("Lathe", "8x16-Inch Mini Precision Lathe"),
    ("Laser Level", "360-Degree Green Laser Level"),
    ("Cordless Screwdriver", "4V Cordless Screwdriver Kit"),
    ("Impact Driver", "20V MAX Lithium Impact Driver"),
    ("Grinding Machine", "100MM 850W Angle Grinding Machine"),
    ("Polisher", "7-Inch Variable Speed Polisher"),
    ("Sander", "5-Inch Random Orbit Sander Kit"),
    ("Caulking Gun", "Cordless Battery-Powered Caulking Gun"),
    ("Tile saw", "10-Inch Wet Saw with Fold Stand"),
    ("Plasma Cutter", "50A CNC Plasma Cutter"),
    ("Welding Machine", "200A MMA AC DC Welding Machine"),
    ("Spot Welder", "2500A Spot Welder for Battery"),
    ("Air Compressor", "6-Gallon 150-PSI Pancake Compressor"),
    ("Pressure Washer", "2030 PSI 2.0 GPM Electric Pressure Washer"),
    ("Generator", "3500W Portable Gas Generator"),
    ("Cleaner", "55L Industrial Vacuum Cleaner"),
    ("Blower", "600W Corded Leaf Blower"),
    ("Pallet Truck", "5500LB Manual Pallet Jack"),
    ("Stacker", "1500KG Electric Stacker"),
]

FILE_TYPES = ["PI", "PL", "CI", "CO", "BL", "DL", "PLATFORM", "SPEC", "MSDS", "CERT"]
LOGISTICS_COMPANIES = ["Maersk", "COSCO", "ONE", "Hapag-Lloyd", "Evergreen", "Yang Ming", "PIL", "ZIM", "MSC", "CMA CGM"]
TRACKING_PREFIXES = ["MSKU", "COSU", "ONEY", "HLCU", "EGLV", "YMLU", "PILU", "ZIMU", "MSCU", "CMDU"]


class Command(BaseCommand):
    help = "Seed demo users, 50 orders, 50 products, and CRM records"

    def handle(self, *args, **options):
        customer, _ = Customer.objects.get_or_create(
            company_name="Manila Forge Industrial Supply",
            defaults={
                "contact_name": "Maria Santos",
                "contact_email": "maria.santos@manilaforge.ph",
                "contact_phone": "+63 917 112 8801",
                "region": "Philippines",
                "status": "enabled",
            },
        )

        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@crm.local",
                "role": User.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "is_enabled": True,
            },
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user"))

        customer_user, created = User.objects.get_or_create(
            username="customer",
            defaults={
                "email": "customer@crm.local",
                "role": User.ROLE_CUSTOMER,
                "customer": customer,
                "is_enabled": True,
            },
        )
        if created:
            customer_user.set_password("customer123")
            customer_user.save()
            self.stdout.write(self.style.SUCCESS("Created customer user"))

        base_date = date(2026, 1, 1)
        statuses = ["pending", "confirmed", "production", "shipped", "completed", "exception"]
        status_weights = [0.1, 0.15, 0.25, 0.2, 0.2, 0.1]

        for i in range(50):
            days_offset = random.randint(0, 105)
            order_date = base_date + timedelta(days=days_offset)

            days_to_eta = random.randint(20, 45)
            eta = order_date + timedelta(days=days_to_eta)

            order_no = f"SO-26{1001 + i:04d}"
            status = random.choices(statuses, weights=status_weights)[0]

            order, created = Order.objects.get_or_create(
                order_no=order_no,
                defaults={
                    "customer": customer,
                    "order_date": order_date,
                    "currency": random.choice(["USD", "PHP", "CNY"]),
                    "amount": f"{random.randint(5000, 150000):.2f}",
                    "eta": eta,
                    "status": status,
                },
            )

            if order.items.exists():
                continue

            prod_name, prod_desc = PRODUCTS[i % len(PRODUCTS)]

            item_count = random.randint(2, 4)
            order_total = Decimal("0")
            for j in range(item_count):
                prod_n, prod_d = PRODUCTS[(i + j) % len(PRODUCTS)]
                sku = f"LT-{prod_n[:2].upper()}-{random.randint(1000, 9999)}"
                qty = random.randint(10, 500)
                unit_price = Decimal(str(round(random.uniform(20, 500), 2)))
                order_total += qty * unit_price
                OrderItem.objects.create(
                    order=order,
                    sku=sku,
                    name=prod_n,
                    spec=prod_d,
                    qty=qty,
                    unit_price=unit_price,
                )

            order.amount = order_total
            order.save(update_fields=["amount"])
            item_types = ["Packaging", "Label", "Manual", "Certification", "Platform", "Material"]
            task_statuses = ["pending", "approved", "revise", "resubmitted"]
            task_status_weights = [0.2, 0.4, 0.2, 0.2]

            task_no = f"CF-26{1001 + i:04d}-01"
            task_status = random.choices(task_statuses, weights=task_status_weights)[0]
            feedbacks = [
                "",
                "Approved for mass production.",
                "Please revise logo color to PMS 123C.",
                "Resubmitted with updated specs.",
                "Need to confirm box dimension.",
                "Please provide battery certification.",
                "Waiting for customer approval on artwork.",
            ]

            ConfirmationTask.objects.get_or_create(
                task_no=task_no,
                defaults={
                    "order": order,
                    "item_type": random.choice(item_types),
                    "item_name": f"{prod_name} - {prod_desc}",
                    "status": task_status,
                    "latest_feedback": random.choice(feedbacks),
                },
            )

            if random.random() > 0.3:
                FileRecord.objects.get_or_create(
                    order=order,
                    file_name=f"PI_{order_no}_v1.pdf",
                    defaults={
                        "file_type": "PI",
                        "file_path": f"/demo/PI_{order_no}_v1.pdf",
                        "version": "v1",
                        "size": f"{random.uniform(0.5, 3.0):.1f} MB",
                        "visibility": "customer",
                        "uploaded_by": admin_user,
                    },
                )

            if status in ["production", "shipped", "completed"]:
                prefix = random.choice(TRACKING_PREFIXES)
                tracking = f"{prefix}{random.randint(2000000, 9999999)}"
                logi_status = (
                    "delivered" if status == "completed"
                    else "inTransit" if random.random() > 0.3
                    else "customs"
                )
                LogisticsRecord.objects.get_or_create(
                    order=order,
                    tracking_no=tracking,
                    defaults={
                        "company": random.choice(LOGISTICS_COMPANIES),
                        "etd": order_date + timedelta(days=random.randint(5, 15)),
                        "eta": eta,
                        "status": logi_status,
                        "latest_note": random.choice([
                            "Loaded at origin port.",
                            "In transit to destination.",
                            "Customs clearance in progress.",
                            "Arrived at destination port.",
                            "Out for delivery.",
                            "Delayed due to weather.",
                            "Container released.",
                        ]),
                    },
                )

            if random.random() > 0.4:
                thread_title = random.choice([
                    f"Order {order_no} Confirmation",
                    f"{prod_name} Artwork Approval",
                    "Production Schedule Update",
                    "Shipping Document Required",
                    "Quality Inspection Request",
                    "Payment Confirmation",
                ])
                thread, _ = MessageThread.objects.get_or_create(
                    customer=customer,
                    order=order,
                    title=thread_title,
                )
                msg_content = random.choice([
                    "Please confirm the production schedule at your earliest convenience.",
                    "We have uploaded the updated artwork for your review.",
                    "Shipping documents have been sent to your email.",
                    "Can you please approve the latest sample photos?",
                    "Payment receipt confirmed. Thank you.",
                    "Please provide the required certifications before shipment.",
                    "We need to discuss the delivery timeline.",
                ])
                MessageRecord.objects.get_or_create(
                    thread=thread,
                    sender=admin_user,
                    defaults={
                        "content": msg_content,
                        "sender_role": "admin",
                        "is_read": random.choice([True, False]),
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            f"Seed completed: 1 customer, 50 orders, order items, 50 confirmation tasks, "
            f"admin/admin123, customer/customer123"
        ))