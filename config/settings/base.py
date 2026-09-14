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
    "apps.staff",
    "apps.contracts",
    "apps.feedback",
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
    "apps.core.security_middleware.SecurityHeadersMiddleware",
    "apps.core.security_middleware.RateLimitMiddleware",
    "apps.core.security_middleware.InputSanitizationMiddleware",
    "apps.core.tenant_middleware.MultiTenantMiddleware",
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
    import dj_database_url
    url = config("DATABASE_URL", default="")
    if url:
        return dj_database_url.parse(url, conn_max_age=600)
    # Fallback to SQLite if no DATABASE_URL (development / unconfigured)
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }


_db = _parse_database_url()
DATABASES = {
    "default": _db
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
    "payment-reminders": {
        "task": "apps.notifications.tasks.send_payment_reminders",
        "schedule": crontab(hour=8, minute=0),  # 8 AM daily
    },
    "upcoming-payment-reminders": {
        "task": "apps.notifications.tasks.send_upcoming_payment_reminders",
        "schedule": crontab(hour=8, minute=30),  # 8:30 AM daily
    },
    "sms-delivery-check": {
        "task": "apps.notifications.tasks.check_sms_delivery_status",
        "schedule": crontab(hour="*/2", minute=0),  # Every 2 hours
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

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Rate limiting
RATE_LIMIT_ENABLED = True

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Logging configuration
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "studioflow.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "security.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "formatter": "verbose",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "errors.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["console", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "security": {
            "handlers": ["console", "security_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "finance": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "notifications.sms": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "ai_fde": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "WARNING",
    },
}
