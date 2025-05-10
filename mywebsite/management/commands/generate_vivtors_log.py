from mywebsite.models import VisitLog, Visitor, Department, SecurityGuard
from django.utils import timezone
import random

# Sample purposes
purposes = [
    "System maintenance",
    "Routine inspection",
    "Supply delivery",
    "Meeting with HR",
    "Equipment repair",
    "IT support visit",
    "Official presentation",
    "Departmental audit",
    "Site tour",
    "Vendor demo"
]

# Get all data
visitors = list(Visitor.objects.all())
departments = Department.objects.all()
guards = list(SecurityGuard.objects.all())

# Safety checks
if not visitors or not departments:
    print("❌ Cannot proceed. Make sure Visitors and Departments exist.")
else:
    for i in range(15):
        visitor = random.choice(visitors)
        dept_index = random.randint(0, departments.count() - 1)
        department = departments[dept_index]
        guard = random.choice(guards) if guards else None
        purpose = random.choice(purposes)

        # Optional badge assignment
        badge_issued = random.choice([True, False])
        badge_number = f"BADGE-{random.randint(1000, 9999)}" if badge_issued else None

        VisitLog.objects.create(
            visitor=visitor,
            purpose=purpose,
            department=department,
            security_guard=guard,
            badge_issued=badge_issued,
            badge_number=badge_number,
            is_inside=True  # Assume visitor is still inside
        )

        print(f"✅ Created VisitLog for {visitor.first_name} to {department.name}")
