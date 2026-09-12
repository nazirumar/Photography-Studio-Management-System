from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.notifications.models import Notification
from apps.notifications.services import (
    delete_old_notifications,
    get_notifications,
    get_unread_count,
    mark_all_read,
    mark_notification_read,
)


@login_required
def notification_list(request):
    unread_only = request.GET.get("unread") == "1"
    notifications = get_notifications(request.user, unread_only=unread_only)
    return render(request, "notifications/list.html", {
        "notifications": notifications,
        "unread_count": get_unread_count(request.user),
        "unread_only": unread_only,
    })


@login_required
def notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    mark_notification_read(notif)
    if notif.link:
        return redirect(notif.link)
    return redirect("notifications:list")


@login_required
def notification_mark_all_read(request):
    if request.method == "POST":
        mark_all_read(request.user)
    return redirect("notifications:list")


@login_required
def notification_unread_count(request):
    count = get_unread_count(request.user)
    return JsonResponse({"unread_count": count})


@login_required
def notification_cleanup(request):
    if request.method == "POST":
        delete_old_notifications()
    return redirect("notifications:list")
