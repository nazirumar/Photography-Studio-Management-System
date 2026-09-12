from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Avg

from apps.projects.models import Project
from apps.projects.feedback_models import Feedback
from apps.clients.models import Client


def feedback_form(request, project_pk):
    """Public feedback form for clients."""
    project = get_object_or_404(Project, pk=project_pk)

    if request.method == "POST":
        rating = request.POST.get("rating")
        photography_quality = request.POST.get("photography_quality")
        service_quality = request.POST.get("service_quality")
        delivery_speed = request.POST.get("delivery_speed")
        comment = request.POST.get("comment", "")
        is_anonymous = request.POST.get("is_anonymous") == "on"

        try:
            client = Client.objects.get(email=request.user.email) if request.user.is_authenticated else project.client
            feedback = Feedback.objects.create(
                project=project,
                client=client,
                rating=int(rating),
                photography_quality=int(photography_quality) if photography_quality else None,
                service_quality=int(service_quality) if service_quality else None,
                delivery_speed=int(delivery_speed) if delivery_speed else None,
                comment=comment,
                is_anonymous=is_anonymous,
                is_public=True,
            )
            messages.success(request, "Thank you for your feedback!")
            return redirect("projects:detail", pk=project.pk)
        except Exception as e:
            messages.error(request, "Error submitting feedback. Please try again.")

    return render(request, "projects/feedback_form.html", {"project": project})


@login_required
def project_feedbacks(request, pk):
    """View all feedback for a project."""
    project = get_object_or_404(Project, pk=pk)
    feedbacks = project.feedbacks.all()

    avg_rating = feedbacks.aggregate(avg=Avg("rating"))["avg"] or 0
    avg_photography = feedbacks.filter(photography_quality__isnull=False).aggregate(avg=Avg("photography_quality"))["avg"] or 0
    avg_service = feedbacks.filter(service_quality__isnull=False).aggregate(avg=Avg("service_quality"))["avg"] or 0
    avg_delivery = feedbacks.filter(delivery_speed__isnull=False).aggregate(avg=Avg("delivery_speed"))["avg"] or 0

    return render(request, "projects/feedbacks.html", {
        "project": project,
        "feedbacks": feedbacks,
        "avg_rating": round(avg_rating, 1),
        "avg_photography": round(avg_photography, 1),
        "avg_service": round(avg_service, 1),
        "avg_delivery": round(avg_delivery, 1),
    })
