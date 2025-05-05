import random
from datetime import timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone

from mywebsite.models import Employee, Attendance

class Command(BaseCommand):
    help = 'Generate attendance for employees with no attendance records for the past 6 months'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=180)

        employees = Employee.objects.filter(employment_status='active')
        employees_without_attendance = [
            emp for emp in employees if not Attendance.objects.filter(employee=emp).exists()
        ]

        total_created = 0

        for employee in employees_without_attendance:
            current_date = six_months_ago

            while current_date <= today:
                if current_date.weekday() < 5:  # Weekdays only
                    status = random.choices(
                        ['present', 'absent', 'half_day'],
                        weights=[0.7, 0.2, 0.1],  # Bias toward present
                        k=1
                    )[0]

                    check_in = check_out = None
                    if status == 'present':
                        check_in = time(hour=random.randint(8, 9), minute=random.randint(0, 59))
                        check_out = time(hour=random.randint(16, 18), minute=random.randint(0, 59))
                    elif status == 'half_day':
                        check_in = time(hour=random.randint(8, 9), minute=random.randint(0, 59))
                        check_out = time(hour=random.randint(12, 13), minute=random.randint(0, 59))

                    Attendance.objects.create(
                        employee=employee,
                        date=current_date,
                        status=status,
                        check_in_time=check_in,
                        check_out_time=check_out
                    )
                    total_created += 1

                current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(
            f"Generated {total_created} attendance records for {len(employees_without_attendance)} employees."
        ))
