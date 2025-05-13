from django.core.management.base import BaseCommand
from mywebsite.models import CCTV, CCTVRecording  # <-- replace with your app name
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generate 5 CCTV and 5 CCTVRecording entries for testing'

    def handle(self, *args, **kwargs):
        locations = ['entrance', 'parking', 'warehouse', 'office', 'production']

        CCTV.objects.all().delete()
        CCTVRecording.objects.all().delete()

        cctv_list = []
        for i in range(5):
            cam = CCTV.objects.create(
                name=f"CCTV-{i+1}",
                location=random.choice(locations),
                ip_address=f"192.168.1.{i+10}",
                is_active=bool(random.getrandbits(1)),
                installation_date=datetime.today().date() - timedelta(days=random.randint(10, 100)),
                last_maintenance=datetime.today().date() - timedelta(days=random.randint(1, 30)),
                description=f"This is camera {i+1} monitoring {locations[i]}"
            )
            cctv_list.append(cam)

        self.stdout.write(self.style.SUCCESS("✔ Created 5 CCTV entries"))

        for i in range(5):
            cctv = random.choice(cctv_list)
            start_time = datetime.now() - timedelta(hours=random.randint(2, 5))
            end_time = start_time + timedelta(minutes=random.randint(5, 20))
            CCTVRecording.objects.create(
                cctv=cctv,
                start_time=start_time,
                end_time=end_time,
                file_path=f"/recordings/cctv_{cctv.id}_clip_{i+1}.mp4",
                incident_reported=bool(random.getrandbits(1)),
                notes="Sample recording clip for testing."
            )

        self.stdout.write(self.style.SUCCESS("✔ Created 5 CCTVRecording entries"))
