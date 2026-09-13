from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from apps.feedback.feedback_service import get_nps_score


def survey_form(request, pk):
    """Public survey form for clients."""
    from apps.feedback.models import Survey
    survey = get_object_or_404(Survey, pk=pk, is_completed=False)

    if request.method == "POST":
        data = {
            "nps_score": int(request.POST.get("nps_score", 0)),
            "overall_rating": int(request.POST.get("overall_rating", 0)),
            "quality_rating": int(request.POST.get("quality_rating", 0)),
            "service_rating": int(request.POST.get("service_rating", 0)),
            "value_rating": int(request.POST.get("value_rating", 0)),
            "would_recommend": request.POST.get("would_recommend") == "yes",
            "feedback_text": request.POST.get("feedback_text", ""),
            "improvements": request.POST.get("improvements", ""),
        }
        from apps.feedback.feedback_service import submit_survey_response
        submit_survey_response(survey, data)
        return render(request, "feedback/thank_you.html")

    return render(request, "feedback/survey_form.html", {"survey": survey})


from django.contrib.auth.decorators import login_required


@login_required
def survey_list(request):
    """Staff view of all surveys."""
    from django.core.paginator import Paginator
    from apps.accounts.services import get_user_studio
    from apps.feedback.models import Survey

    studio = get_user_studio(request.user)
    surveys = Survey.objects.filter(studio=studio).select_related("booking", "booking__client", "booking__package")

    nps = get_nps_score(studio)

    paginator = Paginator(surveys, 20)
    page = request.GET.get("page")
    surveys_page = paginator.get_page(page)

    return render(request, "feedback/list.html", {
        "surveys": surveys_page,
        "nps": nps,
    })
