"""
Django settings for lottery project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from django.urls import reverse_lazy
from djangopwa.cloudinary import config_cloudinary
import os

from lottery import wompi
from lottery.config import BASE_DIR

LANGUAGE_CODE = "es-ES"
USE_I18N = True
USE_L10N = True


PWA_SERVICE_WORKER_PATH = os.path.join(
    BASE_DIR, "djangopwa/static/js", "serviceworker.js"
)


config_cloudinary()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-lf1dwx1fx5dg8zn#ae=7j9y=e3zke6%4(cu)&!ke0qknq9p$6k"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# DEBUG = True

ALLOWED_HOSTS = ["1118257604.pythonanywhere.com"]
# ALLOWED_HOSTS = ["localhost",]


INTERNAL_IPS = [
    "127.0.0.1",
]

# Application definition
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    'django.contrib.auth',
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djangopwa",
    "pwa",
    "tailwind",
    "theme",
    "django_browser_reload",
]

TAILWIND_APP_NAME = "theme"

# SESSION CONFIGURATIONS

SESSION_COOKIE_SECONDS = 60
SESSION_COOKIE_MINUTES = 30
SESSION_COOKIE_AGE = SESSION_COOKIE_MINUTES * SESSION_COOKIE_SECONDS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGIN_URL = "/admin/login/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "djangopwa.middleware.RemoveNextParamMiddleware",
]

JAZZMIN_SETTINGS = {
    "site_tittle": "Admin Sorteos",
    "site_brand": "Panel Admin",
    # "show_ui_builder": True,
    "custom_css": "css/custom_admin.css",
    "custom_js": "js/custom_client_admin.js",
    "hide_models": [
        "djangopwa.Lottery",
        # "djangopwa.ClientInfo",
        "djangopwa.TicketReserved",
        "djangopwa.TicketPurchased",
        "djangopwa.TicketPendingPurchase",
        "djangopwa.TicketWithPayment",
        "djangopwa.Ticket",
        "djangopwa.User",
        "djangopwa.PaymentMethod",
        "djangopwa.TicketAssignment",
        "djangopwa.BankAccount",
        "djangopwa.Payment",
        "djangopwa.PaymentContact",
        "djangopwa.ClientTicketPaymentBalance",
        "djangopwa.Whatsapp",
        "djangopwa.SellerBill",
    ],
    "order_with_respect_to": ["auth"],
    "custom_links": {
        "djangopwa": [
            {
                "name": "Boletas disponibles",
                "url": "admin-tickets-view",
            },
            {
                "name": "Compras pendientes",
                "url": "/admin/djangopwa/ticketpendingpurchase",
            },
            {
                "name": "Boletas con abono",
                "url": "/admin/djangopwa/ticketwithpayment",
            },
            {
                "name": "Boletas reservadas",
                "url": "/admin/djangopwa/ticketreserved",
            },
            {
                "name": "Boletas pagadas",
                "url": "/admin/djangopwa/ticketpurchased",
            },
            {"name": "Reportes", "url": "/admin/reports",
                "permissions": ["auth.view_user"]},
        ],
    },
}

LOGIN_REDIRECT_URL = reverse_lazy("admin-tickets-view")

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-teal",
    "accent": "accent-primary",
    "navbar": "navbar-teal navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-success",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "litera",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": False,
}

ROOT_URLCONF = "lottery.urls"


# settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {  # Log to the console
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # Configure the logger for your application
        'django': {
            'handlers': ['console'],
            'level': 'INFO',  # Set to 'DEBUG' to see all messages
        },
        # You can also define loggers for specific modules or applications
        '__main__': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # "DIRS": [],
        # "DIRS": ["/home/1118257604/lottery/djangopwa/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]


WSGI_APPLICATION = "lottery.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# SQLite Database config
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# PostgreSQL Database config
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "lottery_db",
#         "USER": "postgres",
#         "PASSWORD": "WmuDk6B7saR2p8",
#         "HOST": "localhost",
#         "PORT": "5432",
#     }
# }

# MY SQL config
# DATABASES = {
# 'default': {
# 'ENGINE': 'django.db.backends.mysql',
# 'NAME': '1118257604$lottery_db',
# 'USER': '1118257604',
# 'PASSWORD': 'WmuDk6B7saR2p8',
# 'HOST': '1118257604.mysql.pythonanywhere-services.com',
# }
# }


AUTH_USER_MODEL = "djangopwa.User"


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 4,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Bogota"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"

# Static files directories for PWA apps
# STATICFILES_DIRS = ["/home/1118257604/lottery/static"]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "djangopwa/static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# PWA Configuration
PWA_APP_NAME = "Django PWA"
PWA_APP_DESCRIPTION = "Django app PWA description"
PWA_APP_THEME_COLOR = "#33f3ff"
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_SCOPE = "/"
PWA_APP_ORIENTATION = "any"
PWA_APP_START_URL = "/"
PWA_APP_STATUS_BAR_COLOR = "default"

# PWA_APP_ICONS = [
#     {
#         'src': '/static/images/my_app_icon.png',
#         'sizes': '160x160'
#     }
# ]

PWA_APP_ICONS_APPLE = [
    {"src": "/static/images/my_apple_icon.png", "sizes": "160x160"}]

PWA_APP_SPLASH_SCREEN = [
    {
        "src": "/static/images/icons/splash-640x1136.png",
        "media": "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)",
    }
]

PWA_APP_DIR = "ltr"
PWA_APP_LANG = "en-US"

PWA_APP_SHORTCUTS = [
    {
        "name": "Shortcut",
        "url": "/target",
        "description": "Shortcut to a page in my application",
    }
]

PWA_APP_SCREENSHOTS = [
    {
        "src": "/static/images/icons/splash-750x1334.png",
        "sizes": "750x1334",
        "type": "image/png",
    }
]
