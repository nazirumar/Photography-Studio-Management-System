from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check SMS delivery status from Termii"

    def handle(self, *args, **options):
        from apps.notifications.tasks import check_sms_delivery_status
        check_sms_delivery_status()
        self.stdout.write(self.style.SUCCESS("SMS delivery status checked."))
