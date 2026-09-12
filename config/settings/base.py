from pathlib import Path

from decouple import config
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-production")

DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Third party
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "django_celery_beat",
    "drf_spectacular",
    # Local apps
    "apps.accounts",
    "apps.studios",
    "apps.clients",
    "apps.leads",
    "apps.packages",
    "apps.bookings",
    "apps.projects",
    "apps.gallery",
    "apps.finance",
    "apps.expenses",
    "apps.inventory",
    "apps.equipment",
    "apps.printing",
    "apps.notifications",
    "apps.reports",
    "apps.dashboard",
    "apps.audit",
    "apps.core",
    "apps.portal",
    "apps.api",
    "apps.payments",
    "apps.ai_fde",
    "channels",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

def _parse_database_url():
    url = config("DATABASE_URL", default="studioflow")
    if url.startswith("postgres://") or url.startswith("postgresql://"):
        url = url.split("://", 1)[1]
        user = url.split(":")[0] if ":" in url else "studioflow"
        rest = url.split("@")[1] if "@" in url else url
        password = url.split(":")[1].split("@")[0] if ":" in url and "@" in url else "studioflow"
        host_port = rest.split("/")
        host = host_port[0].split(":")[0] if ":" in host_port[0] else "localhost"
        port = host_port[0].split(":")[1] if ":" in host_port[0] else "5432"
        name = host_port[1] if len(host_port) > 1 else "studioflow"
        return {"NAME": name, "USER": user, "PASSWORD": password, "HOST": host, "PORT": port}
    return {"NAME": url, "USER": "studioflow", "PASSWORD": "studioflow", "HOST": "localhost", "PORT": "5432"}


_db = _parse_database_url()
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _db["NAME"],
        "USER": _db["USER"],
        "PASSWORD": _db["PASSWORD"],
        "HOST": _db["HOST"],
        "PORT": _db["PORT"],
    }
}

AUTH_USER_MODEL = "accounts.User"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Paystack
PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY", default="")
PAYSTACK_PUBLIC_KEY = config("PAYSTACK_PUBLIC_KEY", default="")

# SMS (Termii)
TERMII_API_KEY = config("TERMII_API_KEY", default="")
TERMII_SENDER_ID = config("TERMII_SENDER_ID", default="StudioFlow")

# WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID = config("WHATSAPP_PHONE_NUMBER_ID", default="")
WHATSAPP_ACCESS_TOKEN = config("WHATSAPP_ACCESS_TOKEN", default="")

# AI FDE
AI_ENABLED = config("AI_ENABLED", default="true", cast=bool)
AI_BASE_URL = config("AI_BASE_URL", default="")  # Leave empty for OpenAI, or set to https://api.groq.com/openai/v1 for Groq
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
AI_PRIMARY_MODEL = config("AI_PRIMARY_MODEL", default="gpt-4o")
AI_FAST_MODEL = config("AI_FAST_MODEL", default="gpt-4o-mini")
AI_REASONING_MODEL = config("AI_REASONING_MODEL", default="o3-mini")
AI_EMBEDDING_MODEL = config("AI_EMBEDDING_MODEL", default="BAAI/bge-small-en-v1.5")
AI_MAX_GRAPH_STEPS = config("AI_MAX_GRAPH_STEPS", default=20, cast=int)
AI_REQUEST_TIMEOUT = config("AI_REQUEST_TIMEOUT", default=30, cast=int)
AI_DAILY_USER_LIMIT = config("AI_DAILY_USER_LIMIT", default=100, cast=int)
AI_MONTHLY_STUDIO_LIMIT = config("AI_MONTHLY_STUDIO_LIMIT", default=10000, cast=int)

# LangSmith (optional)
LANGSMITH_ENABLED = config("LANGSMITH_ENABLED", default="false", cast=bool)
LANGSMITH_API_KEY = config("LANGSMITH_API_KEY", default="")
LANGSMITH_PROJECT = config("LANGSMITH_PROJECT", default="studioflow-ai-fde")

# Media
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "StudioFlow API",
    "DESCRIPTION": "Photography Studio Management System API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {"name": "clients", "description": "Client management"},
        {"name": "bookings", "description": "Booking management"},
        {"name": "finance", "description": "Invoices and payments"},
        {"name": "gallery", "description": "Photo galleries"},
        {"name": "projects", "description": "Project tracking"},
        {"name": "inventory", "description": "Inventory management"},
    ],
}

CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_BEAT_SCHEDULE = {
    "daily-backup": {
        "task": "apps.core.tasks.run_daily_backup",
        "schedule": crontab(hour=2, minute=0),  # 2 AM daily
    },
    "weekly-cleanup": {
        "task": "apps.core.tasks.run_weekly_cleanup",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3 AM
    },
    "check-low-stock": {
        "task": "apps.core.tasks.check_low_stock_alerts",
        "schedule": crontab(hour=8, minute=0),  # 8 AM daily
    },
    "check-maintenance": {
        "task": "apps.core.tasks.check_maintenance_alerts",
        "schedule": crontab(hour=8, minute=30),  # 8:30 AM daily
    },
    "booking-reminders": {
        "task": "apps.core.tasks.send_booking_reminders",
        "schedule": crontab(hour=7, minute=0),  # 7 AM daily
    },
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("yo", "Yoruba"),
    ("ig", "Igbo"),
    ("ha", "Hausa"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="StudioFlow <noreply@studioflow.com>")
LOGIN_URL = "/accounts/login/"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "propagate": True,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
