import random
from datetime import timedelta, date

from django.core.management.base import BaseCommand
from django.utils import timezone

from mywebsite.models import (
    ProductVariant, Customer, SalesOrder, SalesOrderItem, Employee
)

from django.db import transaction
from decimal import Decimal


class Command(BaseCommand):
    help = "Generate 20 sales orders for the last 7 days with items"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        product_variants = ProductVariant.objects.filter(status='active')
        customers = Customer.objects.filter(status='active')
        employees = Employee.objects.filter(employment_status='active')

        if not customers.exists() or not product_variants.exists() or not employees.exists():
            self.stdout.write(self.style.ERROR("Ensure active customers, products, and employees exist."))
            return

        total_orders = 0

        for i in range(20):  # Generate 20 orders
            customer = random.choice(customers)
            employee = random.choice(employees)
            order_date = today - timedelta(days=random.randint(0, 6))  # Last 7 days

            order_number = f"SO{random.randint(10000, 99999)}"
            shipping_address = f"{customer.address} - Shipping"
            billing_address = f"{customer.address} - Billing"

            with transaction.atomic():
                order = SalesOrder.objects.create(
                    order_number=order_number,
                    customer=customer,
                    order_date=order_date,
                    status=random.choice(['new', 'processing', 'shipped', 'delivered']),
                    sales_representative=employee,
                    shipping_address=shipping_address,
                    billing_address=billing_address,
                    payment_status=random.choice(['pending', 'partial', 'paid']),
                    delivery_date=order_date + timedelta(days=random.randint(1, 5)),
                    total_amount=0  # placeholder, updated below
                )

                total_amount = Decimal('0.00')

                for _ in range(random.randint(1, 4)):  # 1–4 items per order
                    variant = random.choice(product_variants)
                    quantity = Decimal(random.randint(1, 10))
                    unit_price = Decimal(random.randint(100, 1000))  # Simulated price
                    discount_percent = Decimal(random.choice([0, 5, 10, 15]))
                    subtotal = (quantity * unit_price) * (Decimal('1.0') - discount_percent / 100)

                    SalesOrderItem.objects.create(
                        sales_order=order,
                        product_variant=variant,
                        quantity=quantity,
                        unit_price=unit_price,
                        discount=discount_percent,
                        subtotal=subtotal
                    )

                    total_amount += subtotal

                order.total_amount = total_amount
                order.save()

                total_orders += 1

        self.stdout.write(self.style.SUCCESS(f"Generated {total_orders} sales orders in the past 7 days."))
