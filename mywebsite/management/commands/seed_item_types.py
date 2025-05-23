from django.core.management.base import BaseCommand
from mywebsite.models import ItemType

class Command(BaseCommand):
    help = 'Seeds the database with common item types for visitor/employee logs'

    def handle(self, *args, **kwargs):
        items = [
            # Electronics
            {"name": "Laptop", "description": "Personal or company laptop", "requires_approval": True},
            {"name": "Tablet", "description": "Tablet device used for business or personal use", "requires_approval": True},
            {"name": "Mobile Phone", "description": "Personal mobile phone", "requires_approval": False},
            {"name": "External Hard Drive", "description": "Used to carry data", "requires_approval": True},
            {"name": "USB Flash Drive", "description": "Portable storage device", "requires_approval": True},

            # Tools
            {"name": "Wrench Set", "description": "Used for maintenance or repair", "requires_approval": True},
            {"name": "Screwdriver", "description": "Small tool for adjustments", "requires_approval": True},
            {"name": "Power Drill", "description": "Used by technicians", "requires_approval": True},
            {"name": "Toolbox", "description": "General repair kit", "requires_approval": True},

            # Beverages/Supplies
            {"name": "Coca-Cola Samples", "description": "Company-owned product samples", "requires_approval": True},
            {"name": "Promotional Materials", "description": "Branded t-shirts, flyers", "requires_approval": True},
            {"name": "Merchandise", "description": "Company giveaways or merch", "requires_approval": True},

            # Others
            {"name": "Backpack", "description": "Personal bag", "requires_approval": False},
            {"name": "Helmet", "description": "Safety gear", "requires_approval": False},
            {"name": "Lab Equipment", "description": "Sensitive lab instruments", "requires_approval": True},
            {"name": "First Aid Kit", "description": "Medical kit", "requires_approval": True},
            {"name": "Camera", "description": "For media or surveillance", "requires_approval": True},
            {"name": "Delivery Package", "description": "Items from logistics or delivery", "requires_approval": True},
        ]

        created_count = 0

        for item in items:
            obj, created = ItemType.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "requires_approval": item["requires_approval"]
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Added: {item["name"]}')
            else:
                self.stdout.write(f'Skipped (exists): {item["name"]}')

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} new item types.'))
