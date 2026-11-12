from django.core.management.base import BaseCommand

from apps.accounts.roles import sync_staff_roles


class Command(BaseCommand):
    help = "Create or refresh least-privilege staff role groups."

    def handle(self, *args, **options):
        sync_staff_roles()
        self.stdout.write(self.style.SUCCESS("گروه‌ها و مجوزهای نقش‌های پشتیبانی به‌روزرسانی شدند."))
