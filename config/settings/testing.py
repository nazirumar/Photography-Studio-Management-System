from .base import *  # noqa: F401, F403

DEBUG = False

INSTALLED_APPS += [  # noqa: F405
    "pytest_django",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

AUTH_PASSWORD_VALIDATORS = []

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
