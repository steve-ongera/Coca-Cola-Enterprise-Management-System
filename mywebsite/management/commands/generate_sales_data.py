import random
from decimal import Decimal
from datetime import timedelta, date, datetime
from django.core.management.base import BaseCommand
from mywebsite.models import ProductVariant, SalesOrder, SalesOrderItem, Invoice, Customer, Employee

class Command(BaseCommand):
    help = "Generate random sales orders with invoices (15-25 per month from Jan 2024 to May 2025)"

    def handle(self, *args, **kwargs):
        def random_date_in_month(year, month):
            from calendar import monthrange
            day = random.randint(1, monthrange(year, month)[1])
            return date(year, month, day)

        def generate_code(prefix):
            return f"{prefix}-{random.randint(100000, 999999)}"

        customers = list(Customer.objects.all())
        employees = list(Employee.objects.all())
        product_variants = list(ProductVariant.objects.filter(status='active'))

        if not customers or not employees or not product_variants:
            self.stdout.write(self.style.ERROR("Ensure Customer, Employee, and ProductVariant tables are populated."))
            return

        total_orders = 0
        for year in [2024, 2025]:
            start_month = 1 if year == 2024 else 1
            end_month = 12 if year == 2024 else 5
            for month in range(start_month, end_month + 1):
                num_orders = random.randint(15, 25)
                for _ in range(num_orders):
                    customer = random.choice(customers)
                    employee = random.choice(employees)
                    order_date = random_date_in_month(year, month)

                    sales_order = SalesOrder.objects.create(
                        order_number=generate_code("SO"),
                        customer=customer,
                        order_date=order_date,
                        status=random.choice(['new', 'processing', 'shipped', 'delivered']),
                        sales_representative=employee,
                        shipping_address=f"{customer.name} Residence",
                        billing_address=f"{customer.name} Billing",
                        payment_status=random.choice(['pending', 'partial', 'paid']),
                        delivery_date=order_date + timedelta(days=random.randint(2, 10)),
                        total_amount=0,
                    )

                    total_amount = Decimal("0.00")
                    items_count = random.randint(1, 5)
                    chosen_variants = random.sample(product_variants, min(items_count, len(product_variants)))

                    for variant in chosen_variants:
                        quantity = Decimal(str(random.randint(700, 1300)))
                        unit_price = Decimal(str(variant.selling_price))
                        discount = Decimal(random.choice([0, 5, 10]))
                        subtotal = (unit_price * quantity) * (Decimal("1.00") - (discount / 100))

                        SalesOrderItem.objects.create(
                            sales_order=sales_order,
                            product_variant=variant,
                            quantity=quantity,
                            unit_price=unit_price,
                            discount=discount,
                            subtotal=subtotal
                        )

                        total_amount += subtotal

                    sales_order.total_amount = total_amount
                    sales_order.save()

                    Invoice.objects.create(
                        invoice_number=generate_code("INV"),
                        sales_order=sales_order,
                        invoice_date=order_date + timedelta(days=1),
                        due_date=order_date + timedelta(days=31),
                        status=random.choice(['unpaid', 'partial', 'paid']),
                        payment_terms="Net 30",
                        total_amount=total_amount
                    )

                    total_orders += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully generated {total_orders} sales orders with invoices."))
