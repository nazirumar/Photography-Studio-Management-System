from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog


def create_survey(studio, booking):
    """Create a satisfaction survey for a completed booking."""
    from apps.feedback.models import Survey
    survey, created = Survey.objects.get_or_create(
        studio=studio,
        booking=booking,
        defaults={
            "client_name": str(booking.client),
            "client_email": booking.client.email,
        },
    )
    return survey


def submit_survey_response(survey, data):
    """Submit a client's survey response."""
    from apps.feedback.models import Survey
    with transaction.atomic():
        for field in ["nps_score", "overall_rating", "quality_rating", "service_rating",
                       "value_rating", "would_recommend", "feedback_text", "improvements"]:
            if field in data:
                setattr(survey, field, data[field])
        survey.is_completed = True
        survey.completed_at = timezone.now()
        survey.save()
        return survey


def get_nps_score(studio):
    """Calculate Net Promoter Score for a studio."""
    from django.db.models import Avg, Count, Q
    from apps.feedback.models import Survey

    surveys = Survey.objects.filter(studio=studio, is_completed=True, nps_score__isnull=False)
    total = surveys.count()
    if total == 0:
        return {"score": 0, "promoters": 0, "passives": 0, "detractors": 0, "total": 0}

    promoters = surveys.filter(nps_score__gte=9).count()
    detractors = surveys.filter(nps_score__lte=6).count()
    nps = round(((promoters - detractors) / total) * 100)

    return {
        "score": nps,
        "promoters": round(promoters / total * 100),
        "passives": round((total - promoters - detractors) / total * 100),
        "detractors": round(detractors / total * 100),
        "total": total,
    }
