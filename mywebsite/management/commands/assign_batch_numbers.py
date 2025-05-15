import string
import random
from django.core.management.base import BaseCommand
from mywebsite.models import VisitLog

class Command(BaseCommand):
    help = 'Assign batch numbers to VisitLog entries that are missing them'

    def handle(self, *args, **kwargs):
        logs_without_batch = VisitLog.objects.filter(batch_number__isnull=True)
        updated_count = 0

        for log in logs_without_batch:
            log.batch_number = self.generate_unique_batch_number()
            log.save()
            updated_count += 1
            self.stdout.write(f'Updated VisitLog ID {log.id} with batch number {log.batch_number}')

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} VisitLog entries.'))

    def generate_unique_batch_number(self, length=7):
        characters = string.ascii_uppercase + string.digits
        while True:
            batch = ''.join(random.choices(characters, k=length))
            if not VisitLog.objects.filter(batch_number=batch).exists():
                return batch
