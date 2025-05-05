import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from mywebsite.models import Leave, Employee

User = get_user_model()

class Command(BaseCommand):
    help = "Generate 2–4 leave requests per employee for each month in the past 6 months"

    def handle(self, *args, **kwargs):
        employees = Employee.objects.filter(employment_status='active')
        approvers = User.objects.filter(is_staff=True)

        if not employees.exists() or not approvers.exists():
            self.stdout.write(self.style.ERROR("No employees or approvers found."))
            return

        today = date.today()
        for months_ago in range(6):
            month_start = (today.replace(day=1) - timedelta(days=months_ago * 30)).replace(day=1)
            month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

            for emp in employees:
                for _ in range(random.randint(2, 4)):
                    start_offset = random.randint(0, (month_end - month_start).days - 3)
                    start_date = month_start + timedelta(days=start_offset)
                    end_date = start_date + timedelta(days=random.randint(1, 3))
                    if end_date > month_end:
                        end_date = month_end

                    Leave.objects.create(
                        employee=emp,
                        leave_type=random.choice([lt[0] for lt in Leave.LEAVE_TYPE_CHOICES]),
                        start_date=start_date,
                        end_date=end_date,
                        reason="Auto-generated leave",
                        status=random.choice(['approved', 'pending']),
                        approved_by=random.choice(approvers)
                    )

        self.stdout.write(self.style.SUCCESS("Leaves generated for the last 6 months."))
