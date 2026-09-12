from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path


def logout_view(request):
    logout(request)
    from django.conf import settings
    return redirect(settings.LOGOUT_REDIRECT_URL)


app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
]
