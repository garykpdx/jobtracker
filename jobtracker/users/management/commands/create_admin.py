import environ
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

env = environ.Env()


class Command(BaseCommand):
    help = "Creates a superuser from environment variables if one doesn't already exist"

    def handle(self, *args, **options):
        User = get_user_model()
        username = env("DJANGO_SUPERUSER_USERNAME", default=None)
        email = env("DJANGO_SUPERUSER_EMAIL", default=None)
        password = env("DJANGO_SUPERUSER_PASSWORD", default=None)

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                "Skipping superuser creation: missing DJANGO_SUPERUSER_* env vars"
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists"))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created"))
