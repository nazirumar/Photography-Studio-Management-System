from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate and cache business reports"

    def handle(self, *args, **options):
        from apps.reports.forecast_service import get_revenue_forecast
        from apps.studios.models import Studio
        
        for studio in Studio.objects.all():
            forecast = get_revenue_forecast(studio)
            self.stdout.write(
                f"Studio: {studio.name} | "
                f"Avg Monthly: N{forecast['avg_monthly']:,.0f} | "
                f"Growth: {forecast['growth_rate']}%"
            )
        self.stdout.write(self.style.SUCCESS("Reports generated."))
