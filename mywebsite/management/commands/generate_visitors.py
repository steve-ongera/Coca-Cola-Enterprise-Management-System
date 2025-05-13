import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from mywebsite.models import Visitor, VisitLog, Department, SecurityGuard  # Replace 'your_app' with actual app name

KENYAN_FIRST_NAMES = [
    "Stephen", "Faith", "Brian", "Mercy", "George", "Janet", "Collins", "Diana", "Kevin", "Lucy",
    "James", "Brenda", "Samuel", "Alice", "Peter", "Agnes", "John", "Mary", "Daniel", "Naomi"
]

KENYAN_LAST_NAMES = [
    "Ongera", "Otieno", "Wanjiru", "Mwangi", "Njoroge", "Atieno", "Odhiambo", "Kariuki", "Mutiso", "Kimani",
    "Ouma", "Wambui", "Were", "Njuguna", "Chebet", "Cheruiyot", "Barasa", "Makori", "Moraa", "Kiprotich"
]

COMPANIES = [
    "Safaricom Ltd", "Equity Bank", "KPLC", "KCB Group", "EABL", "Nation Media", "KenGen", "Jumia Kenya", 
    "Kenya Airways", "Naivas Supermarket"
]

PURPOSES = [
    "Meeting with department head", "Delivering documents", "Routine maintenance", "Vendor appointment",
    "Contract signing", "Inspection", "System upgrade discussion", "Guest lecture", "Job interview"
]

VISITOR_TYPES = ['contractor', 'vendor', 'guest', 'official']

ID_TYPES = ['National ID', 'Passport', 'Driving License']


class Command(BaseCommand):
    help = 'Generate sample visitor and visit log data from May last year to May this year'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        start_date = today.replace(day=1) - relativedelta(months=12)

        departments = list(Department.objects.all())
        guards = list(SecurityGuard.objects.all())

        if not departments or not guards:
            self.stdout.write(self.style.ERROR("Ensure departments and security guards exist in the database."))
            return

        current_month = start_date

        while current_month <= today.replace(day=1):
            num_visitors = random.randint(15, 25)
            self.stdout.write(f"Creating {num_visitors} visitors for {current_month.strftime('%B %Y')}...")

            for _ in range(num_visitors):
                first_name = random.choice(KENYAN_FIRST_NAMES)
                last_name = random.choice(KENYAN_LAST_NAMES)
                company = random.choice(COMPANIES)
                email = f"{first_name.lower()}.{last_name.lower()}@{company.split()[0].lower()}.co.ke"
                phone = f"07{random.randint(10,99)}{random.randint(100000,999999)}"
                id_number = f"{random.randint(10000000, 99999999)}"
                id_type = random.choice(ID_TYPES)
                visitor_type = random.choice(VISITOR_TYPES)

                visitor = Visitor.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    company=company,
                    email=email,
                    phone=phone,
                    id_number=id_number,
                    id_type=id_type,
                    visitor_type=visitor_type
                )

                department = random.choice(departments)
                security_guard = random.choice(guards)

                # Random date in the current month
                visit_date = current_month + timedelta(days=random.randint(0, 27))
                check_in = timezone.make_aware(datetime.combine(visit_date, datetime.min.time()) + timedelta(hours=random.randint(8, 16)))
                check_out = check_in + timedelta(hours=random.randint(1, 4))

                VisitLog.objects.create(
                    visitor=visitor,
                    purpose=random.choice(PURPOSES),
                    department=department,
                    security_guard=security_guard,
                    check_in_time=check_in,
                    check_out_time=check_out,
                    badge_issued=True,
                    badge_number=f"B-{random.randint(1000,9999)}",
                    is_inside=False
                )

            current_month += relativedelta(months=1)

        self.stdout.write(self.style.SUCCESS("Visitor data generation complete."))
