from django.urls import path
from . import debug_views

urlpatterns = [
    path("", debug_views.debug_login, name="debug_login"),
    path("post/", debug_views.debug_post_login, name="debug_post_login"),
]
