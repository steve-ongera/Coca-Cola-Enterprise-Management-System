import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from mywebsite.models import VisitLog  # Replace with your actual app name

class Command(BaseCommand):
    help = 'Randomize check-in and check-out times for existing VisitLogs'

    def handle(self, *args, **kwargs):
        today = timezone.now()
        start_date = (today - relativedelta(months=12)).replace(day=1)

        logs = VisitLog.objects.all()
        total = logs.count()

        if not total:
            self.stdout.write(self.style.WARNING("No VisitLogs to update."))
            return

        self.stdout.write(f"Updating {total} VisitLog entries...")

        for log in logs:
            # Generate random check-in date between start_date and today
            random_days = random.randint(0, (today - start_date).days)
            check_in = start_date + timedelta(days=random_days, hours=random.randint(8, 15))

            # Ensure check_in is naive and then make it aware if needed
            if timezone.is_naive(check_in):
                check_in = timezone.make_aware(check_in)

            # Random check-out time between 1 and 6 hours after check-in
            check_out = check_in + timedelta(hours=random.randint(1, 6))

            # Ensure check_out is naive and then make it aware if needed
            if timezone.is_naive(check_out):
                check_out = timezone.make_aware(check_out)

            log.check_in_time = check_in
            log.check_out_time = check_out
            log.is_inside = False  # Mark all as checked out for consistency

            # Save without triggering notification
            VisitLog.objects.filter(pk=log.pk).update(
                check_in_time=log.check_in_time,
                check_out_time=log.check_out_time,
                is_inside=log.is_inside
            )

        self.stdout.write(self.style.SUCCESS("VisitLog times updated successfully."))
