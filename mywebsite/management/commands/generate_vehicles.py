import random
import string
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from mywebsite.models import Vehicle, VehicleLog, Visitor, SecurityGuard  # Replace with your actual app name
from django.contrib.auth import get_user_model

User = get_user_model()

MAKES_MODELS = {
    "Toyota": ["Corolla", "Hilux", "Prado", "Fielder", "Vitz"],
    "Nissan": ["Navara", "Note", "X-Trail", "March"],
    "Mazda": ["Demio", "CX-5", "Atenza"],
    "Mitsubishi": ["Outlander", "Canter", "Lancer"],
    "Isuzu": ["D-Max", "N-Series"],
    "Subaru": ["Forester", "Impreza", "Legacy"],
    "Honda": ["Fit", "Civic", "CR-V"]
}

COLORS = [
    "White", "Black", "Silver", "Blue", "Red", "Green", "Grey", "Maroon", "Beige"
]

VEHICLE_TYPES = ['employee', 'visitor', 'delivery', 'company']
PURPOSES = [
    "Delivery of goods", "Employee commuting", "Management transport", 
    "Official trip", "Vendor drop-off", "Visitor parking"
]

class Command(BaseCommand):
    help = 'Generate vehicle entries from May last year to May this year'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        start_date = today.replace(month=5, day=1) - relativedelta(years=1)
        end_date = today.replace(day=1)

        guards = list(SecurityGuard.objects.all())
        visitors = list(Visitor.objects.all())
        users = list(User.objects.all())

        if not guards:
            self.stdout.write(self.style.ERROR("Add at least one security guard before running this."))
            return

        current_month = start_date
        used_plates = set(Vehicle.objects.values_list('license_plate', flat=True))

        while current_month <= end_date:
            num_vehicles = random.randint(8, 12)
            self.stdout.write(f"Generating {num_vehicles} vehicles for {current_month.strftime('%B %Y')}...")

            for _ in range(num_vehicles):
                make = random.choice(list(MAKES_MODELS.keys()))
                model = random.choice(MAKES_MODELS[make])
                color = random.choice(COLORS)
                vehicle_type = random.choice(VEHICLE_TYPES)

                # Generate unique Kenyan license plate (e.g., KBA 123C)
                while True:
                    letter1 = random.choice(['A', 'B', 'C', 'D', 'K', 'Z'])
                    letter2 = random.choice(string.ascii_uppercase)
                    number = random.randint(100, 999)
                    suffix = random.choice(string.ascii_uppercase)
                    plate = f"K{letter1}{letter2} {number}{suffix}"
                    if plate not in used_plates:
                        used_plates.add(plate)
                        break

                owner = random.choice(users) if vehicle_type == 'employee' else None
                visitor_owner = random.choice(visitors) if vehicle_type == 'visitor' else None

                vehicle = Vehicle.objects.create(
                    license_plate=plate,
                    make=make,
                    model=model,
                    color=color,
                    vehicle_type=vehicle_type,
                    owner=owner,
                    visitor_owner=visitor_owner
                )

                visit_date = current_month + timedelta(days=random.randint(0, 27))
                entry_time = timezone.make_aware(datetime.combine(visit_date, datetime.min.time()) + timedelta(hours=random.randint(7, 17)))
                exit_time = entry_time + timedelta(hours=random.randint(1, 4))

                VehicleLog.objects.create(
                    vehicle=vehicle,
                    entry_time=entry_time,
                    exit_time=exit_time,
                    security_guard=random.choice(guards),
                    purpose=random.choice(PURPOSES),
                    is_inside=False
                )

            current_month += relativedelta(months=1)

        self.stdout.write(self.style.SUCCESS("✅ Vehicle data generation complete."))
