
from mywebsite.models import SecurityGuard
from datetime import time
import random
from django.contrib.auth import get_user_model
User = get_user_model()


# Sample Kenyan names
kenyan_names = [
    ("James", "Mwangi"),
    ("Mary", "Wanjiku"),
    ("John", "Ouma"),
    ("Grace", "Achieng"),
    ("Peter", "Kiptoo"),
    ("Jane", "Nyambura"),
    ("Daniel", "Mutiso"),
    ("Cynthia", "Atieno"),
    ("Samuel", "Chege"),
    ("Rose", "Wambui")
]

# Shift time slots (hour only)
shift_slots = [
    (time(6, 0), time(14, 0)),   # Morning shift
    (time(14, 0), time(22, 0)),  # Afternoon shift
    (time(22, 0), time(6, 0)),   # Night shift
]

# Check how many guards already exist
existing_guards = SecurityGuard.objects.count()
guards_to_create = 10 - existing_guards

for i in range(guards_to_create):
    first_name, last_name = kenyan_names[i]
    username = f"{first_name.lower()}{last_name.lower()}"
    email = f"{username}@gmail.com"
    password = "cp7kvt"

    # Create user
    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
    )

    # Assign shift
    shift_start, shift_end = shift_slots[i % len(shift_slots)]

    # Create SecurityGuard
    SecurityGuard.objects.create(
        user=user,
        badge_number=f"SG2025{i+1:03d}",
        shift_start=shift_start,
        shift_end=shift_end,
        is_active=True
    )

    print(f"Created SecurityGuard: {first_name} {last_name} - SG2025{i+1:03d}")
