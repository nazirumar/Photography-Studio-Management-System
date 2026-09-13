from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Send payment reminders for overdue invoices"

    def handle(self, *args, **options):
        from apps.notifications.tasks import send_payment_reminders, send_upcoming_payment_reminders
        send_payment_reminders()
        send_upcoming_payment_reminders()
        self.stdout.write(self.style.SUCCESS("Payment reminders sent."))
