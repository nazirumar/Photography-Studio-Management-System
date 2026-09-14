from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from django.contrib.auth import authenticate, login


@csrf_exempt
@require_GET
def debug_login(request):
    """Test if login works. Remove after debugging."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user_count = User.objects.count()
        staff_count = User.objects.filter(is_staff=True).count()
        return JsonResponse({
            "status": "ok",
            "user_count": user_count,
            "staff_count": staff_count,
            "debug": getattr(request, "_debug_info", {}),
        })
    except Exception as e:
        return JsonResponse({"error": str(e), "type": type(e).__name__}, status=500)


@csrf_exempt
def debug_post_login(request):
    """Test if POST login works."""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        email = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"status": "ok", "logged_in": True, "email": user.email})
        return JsonResponse({"status": "ok", "logged_in": False, "reason": "invalid_credentials"})
    except Exception as e:
        import traceback
        return JsonResponse({
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
        }, status=500)
