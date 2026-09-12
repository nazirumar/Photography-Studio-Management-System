from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import PortalLoginForm, PortalProfileForm
from .models import ClientUser


def portal_login_view(request):
    """Client portal login."""
    if request.user.is_authenticated:
        if hasattr(request.user, "clientuser"):
            return redirect("portal:dashboard")
        return redirect("/")

    if request.method == "POST":
        form = PortalLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, "Welcome to your portal!")
            return redirect("portal:dashboard")
        else:
            messages.error(request, "Invalid email or password")
    else:
        form = PortalLoginForm()

    return render(request, "portal/login.html", {"form": form})


def portal_logout_view(request):
    """Client portal logout."""
    logout(request)
    return redirect("portal:login")


@login_required
def portal_profile(request):
    """Client portal - edit profile."""
    try:
        client_user = ClientUser.objects.get(pk=request.user.pk)
    except ClientUser.DoesNotExist:
        return redirect("portal:dashboard")

    if request.method == "POST":
        form = PortalProfileForm(request.POST)
        if form.is_valid():
            client_user.first_name = form.cleaned_data["first_name"]
            client_user.last_name = form.cleaned_data["last_name"]
            client_user.save(update_fields=["first_name", "last_name"])
            messages.success(request, "Profile updated!")
            return redirect("portal:dashboard")
    else:
        form = PortalProfileForm(initial={
            "first_name": client_user.first_name,
            "last_name": client_user.last_name,
            "phone": client_user.client.phone if client_user.client else "",
        })

    return render(request, "portal/profile.html", {"form": form, "client_user": client_user})
