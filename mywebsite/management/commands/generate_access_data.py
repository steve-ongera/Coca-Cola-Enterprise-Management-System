from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from mywebsite.models import Door, BiometricData, AccessLog
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generate sample data for Users, Doors, BiometricData, and AccessLogs'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Clear old test data
        Door.objects.all().delete()
        BiometricData.objects.all().delete()
        AccessLog.objects.all().delete()
        User.objects.filter(username__startswith="user").delete()

        # Create users
        users = []
        for i in range(5):
            user = User.objects.create_user(username=f"user{i+1}", password="cp7kvt")
            users.append(user)

        # Create doors
        doors = []
        locations = ['Main Gate', 'Server Room', 'Warehouse', 'HR Office', 'Lab']
        for i in range(5):
            door = Door.objects.create(
                name=f"Door {i+1}",
                location=locations[i],
                is_active=True
            )
            doors.append(door)

        # Create biometric data
        biometric_types = ['FINGERPRINT', 'FACE', 'IRIS', 'VOICE']
        for user in users:
            BiometricData.objects.create(
                user=user,
                biometric_type=random.choice(biometric_types),
                template_data=b'sample_binary_data'
            )

        # Create access logs
        for _ in range(10):
            user = random.choice(users)
            door = random.choice(doors)
            access_granted = random.choice([True, False])
            biometric_used = random.choice(biometric_types)

            AccessLog.objects.create(
                user=user,
                door=door,
                access_time=timezone.now(),
                access_granted=access_granted,
                biometric_used=biometric_used
            )

        self.stdout.write(self.style.SUCCESS("✔ Sample access control data generated successfully."))
