from django.core.management.base import BaseCommand
from faker import Faker
import random

from ...models import Property, User

fake = Faker()


class Command(BaseCommand):
    help = "Seed fake properties"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creating fake properties...")

        admin = User.objects.filter(is_superuser=True).first()

        if not admin:
            self.stdout.write(self.style.ERROR("No admin user found. Create one first."))
            return

        properties = []

        for _ in range(20):
            price = random.randint(50000, 500000)

            property = Property.objects.create(
                title=fake.catch_phrase(),
                location=fake.city(),
                price=price,
                discount=random.randint(0, int(price * 0.2)),
                description=fake.text(max_nb_chars=150),
                created_by=admin
            )

            properties.append(property)

        self.stdout.write(self.style.SUCCESS(f"{len(properties)} properties created successfully!"))