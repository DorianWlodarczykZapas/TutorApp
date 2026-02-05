import os
from pathlib import Path
from typing import List

import environ
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent


env = environ.Env(DEBUG=(bool, False))
env.read_env(BASE_DIR / ".env")


AUTH_USER_MODEL = "users.User"


SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS: List[str] = ["*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "silk",
    "debug_toolbar",
    "django_extensions",
    "django_filters",
    "django_select2",
    "crispy_forms",
    "crispy_bootstrap5",
]

INSTALLED_EXTENSIONS = [
    "users",
    "plans",
    "examination_tasks",
    "quizes",
    "training_calendar",
    "videos",
    "motifs",
    "courses",
]

INSTALLED_APPS += INSTALLED_EXTENSIONS

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "DevApp <dev@example.com>"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "silk.middleware.SilkyMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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


WSGI_APPLICATION = "core.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("PG_NAME"),
        "USER": env("PG_USER"),
        "PASSWORD": env("PG_PASSWORD"),
        "HOST": env("PG_HOST", default="localhost"),
        "PORT": env("PG_PORT", default="5432"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("pl", _("Polish")),
    ("en", _("English")),
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_ROOT = BASE_DIR / "media"


MEDIA_URL = "/media/"

TEMP_WIZARD_DIR = os.path.join(MEDIA_ROOT, "temp_wizard")
TEMP_PREVIEW_DIR = os.path.join(MEDIA_ROOT, "temp_previews")

INTERNAL_IPS = [
    "127.0.0.1",
]

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/1")

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
