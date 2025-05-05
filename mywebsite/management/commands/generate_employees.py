import random
from django.core.management.base import BaseCommand
from mywebsite.models import Employee, Department
from datetime import date, timedelta
from django.contrib.auth import get_user_model
User = get_user_model()


KENYAN_FIRST_NAMES_MALE = [
    "Brian", "Kevin", "Samuel", "Joseph", "Peter", "Daniel", "George", "John", "David", "Collins",
    "Elvis", "Eric", "Francis", "James", "Kennedy", "Emmanuel", "Anthony", "Michael", "Andrew", "Simon"
]

KENYAN_FIRST_NAMES_FEMALE = [
    "Faith", "Grace", "Mercy", "Eunice", "Janet", "Caroline", "Ann", "Joyce", "Lucy", "Diana",
    "Brenda", "Dorothy", "Agnes", "Esther", "Beatrice", "Catherine", "Ruth", "Lilian", "Nancy", "Sarah"
]

KENYAN_LAST_NAMES = [
    "Omondi", "Wafula", "Mwangi", "Njoroge", "Otieno", "Kiptoo", "Mutiso", "Kariuki", "Mugo", "Kimani",
    "Koech", "Odhiambo", "Wambua", "Maina", "Nyambura", "Cherono", "Ochieng", "Obiero", "Munyiri", "Makau"
]

POSITIONS = [pos[0] for pos in Employee.POSITION_CHOICES]
ROLES = [role[0] for role in Employee.ROLE_CHOICES]
EMPLOYMENT_STATUSES = [status[0] for status in Employee.EMPLOYMENT_STATUS_CHOICES]
CONTRACT_TYPES = ['permanent', 'contract']

class Command(BaseCommand):
    help = 'Generate 200 Kenyan employees without using faker'

    def handle(self, *args, **kwargs):
        departments = list(Department.objects.all())

        for i in range(200):
            gender = random.choice(['male', 'female'])
            first_name = random.choice(KENYAN_FIRST_NAMES_MALE if gender == 'male' else KENYAN_FIRST_NAMES_FEMALE)
            last_name = random.choice(KENYAN_LAST_NAMES)

            username = f"{first_name.lower()}{last_name.lower()}{random.randint(10,999)}"
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1,999)}@gmail.com"
            phone_number = f"07{random.randint(0,9)}{random.randint(1000000,9999999)}"
            emergency_contact_number = f"07{random.randint(0,9)}{random.randint(1000000,9999999)}"
            emergency_contact_name = f"{random.choice(KENYAN_FIRST_NAMES_MALE + KENYAN_FIRST_NAMES_FEMALE)} {random.choice(KENYAN_LAST_NAMES)}"
            
            hire_date = date.today() - timedelta(days=random.randint(30, 1095))  # within last 3 years
            date_of_birth = date.today() - timedelta(days=random.randint(22*365, 60*365))  # age 22-60
            salary = round(random.uniform(30000, 150000), 2)
            bank_account_number = str(random.randint(1000000000, 9999999999))
            department = random.choice(departments) if departments else None

            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='12345678'
            )

            # Create the employee
            Employee.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_number=emergency_contact_number,
                hire_date=hire_date,
                employment_status=random.choice(EMPLOYMENT_STATUSES),
                contract_type=random.choice(CONTRACT_TYPES),
                position=random.choice(POSITIONS),
                role=random.choice(ROLES),
                department=department,
                phone_number=phone_number,
                address="Nairobi, Kenya",
                salary=salary,
                bank_account_number=bank_account_number,
                date_of_birth=date_of_birth
            )

        self.stdout.write(self.style.SUCCESS("✅ Successfully generated 200 Kenyan employees."))
