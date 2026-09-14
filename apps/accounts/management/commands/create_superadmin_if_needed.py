import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create initial superadmin if no users exist"

    def handle(self, *args, **options):
        from apps.accounts.models import User

        if User.objects.filter(is_staff=True).exists():
            self.stdout.write(self.style.SUCCESS("Admin user already exists, skipping."))
            return

        email = os.environ.get("ADMIN_EMAIL", "admin@studioflow.com")
        password = os.environ.get("ADMIN_PASSWORD", "admin123")

        if not User.objects.exists():
            studio = None
            from apps.studios.models import Studio

            studio, _ = Studio.objects.get_or_create(
                name=os.environ.get("STUDIO_NAME", "Lagos Photography Studio"),
                defaults={"slug": "lagos-studio", "phone": "+234-800-000-0000", "email": email},
            )
        else:
            studio = None

        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name="Admin",
            last_name="User",
            studio=studio,
        )
        self.stdout.write(self.style.SUCCESS(f"Created superadmin: {email}"))
