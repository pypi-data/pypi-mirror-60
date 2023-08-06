"""
Base settings to build other settings files upon.
"""

import environ

ROOT_DIR = (
    environ.Path(__file__) - 3
)  # (zonesmart/config/settings/base.py - 3 = zonesmart/)
APPS_DIR = ROOT_DIR.path("zonesmart")

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

# GENERAL
# ------------------------------------------------------------------------------
APPEND_SLASH = False
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/Moscow"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "ru-ru"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = False
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [ROOT_DIR.path("locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

# DATABASES = {"default": env.db("DATABASE_URL")}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}

DATABASES["default"]["ATOMIC_REQUESTS"] = True

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls.root"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "django_celery_beat",
    "cities_light",  # https://github.com/yourlabs/django-cities-light
    "nested_admin",  # https://django-nested-admin.readthedocs.io/en/latest/
    "admin_reorder",
    "storages",
    "rest_framework",  # https://github.com/encode/django-rest-framework
    "django_filters",  # https://github.com/carltongibson/django-filter
    "djoser",  # https://github.com/sunscrapers/djoser
    "multiselectfield",  # https://github.com/goinnn/django-multiselectfield
    "corsheaders",  # https://github.com/adamchainz/django-cors-headers
    "rest_framework_nested",  # https://github.com/alanjds/drf-nested-routers
]

LOCAL_APPS = [
    # ZoneSmart
    "zonesmart",
    "zonesmart.users",
    "zonesmart.marketplace",
    "zonesmart.category",
    "zonesmart.product",
    "zonesmart.order",
    "zonesmart.support",
    "zonesmart.news",
    # Ebay
    "ebay",
    "ebay.account",
    "ebay.location",
    "ebay.category",
    "ebay.listing",
    "ebay.order",
    "ebay.policy",
    "ebay.negotiation",
    "ebay.feed",
    # Amazon
    "amazon",
    "amazon.account",
    "amazon.category",
    "amazon.product",
    "amazon.order",
    # Etsy
    "etsy",
    "etsy.account",
    "etsy.category",
    "etsy.policy",
    "etsy.listing",
    "etsy.order",
]

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "zonesmart.contrib.sites.migrations"}

# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "jwt:jwt-create"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "admin_reorder.middleware.ModelAdminReorder",
]

# STORAGES
# ------------------------------------------------------------------------------
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_STORAGE_BUCKET_NAME = env("DJANGO_AWS_STORAGE_BUCKET_NAME")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_QUERYSTRING_AUTH = False
# DO NOT change these unless you know what you're doing.
_AWS_EXPIRY = 60 * 60 * 24 * 7
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate"
}
#  https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_DEFAULT_ACL = None
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_REGION_NAME = env("DJANGO_AWS_S3_REGION_NAME", default=None)
AWS_S3_ENDPOINT_URL = env("DJANGO_AWS_S3_ENDPOINT_URL")
AWS_LOCATION = env("DJANGO_AWS_LOCATION")
AWS_MEDIA_ROOT = env("DJANGO_AWS_MEDIA_ROOT")
AWS_HEADERS = {
    "Cache-Control": "max-age=86400, s-maxage=86400, must-revalidate",
}


# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = []
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("media"))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{AWS_MEDIA_ROOT}/"


# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR.path("templates"))],
        # "DIRS": [],
        # "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
# https://docs.djangoproject.com/en/2.2/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""zonesmart""", "noreply@zonesmart.ru")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-timezone
    CELERY_TIMEZONE = TIME_ZONE
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_url
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_backend
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-accept_content
CELERY_ACCEPT_CONTENT = ["json"]
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_serializer
CELERY_TASK_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-result_serializer
CELERY_RESULT_SERIALIZER = "json"
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_TIME_LIMIT = 5 * 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-soft-time-limit
# TODO: set to whatever value is adequate in your circumstances
CELERY_TASK_SOFT_TIME_LIMIT = 60
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#beat-scheduler
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# Additional settings
# ------------------------------------------------------------------------------
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False

LOG_DIR = ROOT_DIR.path("logs")


# eBay API settings
# ------------------------------------------------------------------------------

EBAY_SANDBOX = False

USER_SANDBOX_API_SCOPES = [
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.account",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    "https://api.ebay.com/oauth/api_scope/sell.marketing",
    "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.marketplace.insights.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.finances",
    "https://api.ebay.com/oauth/api_scope/sell.item",
    "https://api.ebay.com/oauth/api_scope/sell.item.draft",
    "https://api.ebay.com/oauth/api_scope/sell.payment.dispute",
    "https://api.ebay.com/oauth/api_scope/commerce.catalog.readonly",
    "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly",
]

APP_SANDBOX_API_SCOPES = [
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/buy.guest.order",
    "https://api.ebay.com/oauth/api_scope/buy.item.feed",
    "https://api.ebay.com/oauth/api_scope/buy.marketing",
    "https://api.ebay.com/oauth/api_scope/buy.product.feed",
    "https://api.ebay.com/oauth/api_scope/buy.marketplace.insights",
    "https://api.ebay.com/oauth/api_scope/buy.proxy.guest.order",
]

USER_PRODUCTION_API_SCOPES = [
    "https://api.ebay.com/oauth/api_scope",
    "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.marketing",
    "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.inventory",
    "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.account",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
    "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.finances",
    "https://api.ebay.com/oauth/api_scope/sell.payment.dispute",
    "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly",
]

APP_PRODUCTION_API_SCOPES = [
    "https://api.ebay.com/oauth/api_scope",
]

EBAY_APP_CONFIG = {
    "production": {
        "dev_id": env("PRODUCTION_DEV_ID"),
        "client_secret": env("PRODUCTION_CERT_ID"),
        "ru_name": env("PRODUCTION_REDIRECT_URI"),
        "client_id": env("PRODUCTION_APP_ID"),
    },
    "sandbox": {
        "dev_id": env("SANDBOX_DEV_ID"),
        "client_secret": env("SANDBOX_CERT_ID"),
        "ru_name": env("SANDBOX_REDIRECT_URI"),
        "client_id": env("SANDBOX_APP_ID"),
    },
}

EBAY_API_REQUEST_TIMEOUT = 30


# Amazon API settings
# ------------------------------------------------------------------------------

AMAZON_APP_CONFIG = {
    "access_key": env("AMAZON_ACCESS_KEY"),
    "secret_key": env("AMAZON_SECRET_KEY"),
    "account_id": env("AMAZON_ACCOUNT_ID"),
    "developer_id": env("AMAZON_DEVELOPER_ID"),
}

# Etsy API settings
# ------------------------------------------------------------------------------

ETSY_APP_CONFIG = {
    "app_name": env("ETSY_APP_NAME"),
    "api_key": env("ETSY_API_KEY"),
    "secret": env("ETSY_SECRET_KEY"),
}

ETSY_SANDBOX = False

ETSY_OAUTH_CALLBACK = "https://zonesmart.ru/etsy/account/"

ETSY_API_SCOPES = [
    "email_r",
    "listings_r",
    "listings_w",
    "listings_d",
    "transactions_r",
    "transactions_w",
    "billing_r",
    "profile_r",
    "profile_w",
    "address_r",
    "address_w",
    "favorites_rw",
    "shops_rw",
    "cart_rw",
    "recommend_rw",
    "feedback_r",
]


# cities_light settings
# ------------------------------------------------------------------------------

# absolute path to download and extract data into
CITIES_LIGHT_DATA_DIR = ROOT_DIR.path("zonesmart", "data", "cities_light").root

# lang codes http://download.geonames.org/export/dump/iso-languagecodes.txt
CITIES_LIGHT_TRANSLATION_LANGUAGES = ["ru", "en"]

CITIES_LIGHT_INCLUDE_COUNTRIES = ["US", "RU"]

# city types codes http://www.geonames.org/export/codes.html
CITIES_LIGHT_INCLUDE_CITY_TYPES = [
    "PPL",
    "PPLA",
    "PPLA2",
    "PPLA3",
    "PPLA4",
    "PPLC",
    "PPLF",
    "PPLG",
    "PPLL",
    "PPLS",
]


# Admin reorder settings
# ------------------------------------------------------------------------------
ADMIN_REORDER = (
    "support",
    {
        "app": "users",
        "label": "Пользователи и права доступа",
        "models": (
            {"model": "users.User", "label": "Пользователи"},
            {"model": "auth.Group", "label": "Группы"},
        ),
    },
    "marketplace",
    # app
    "ebay",
    "amazon",
    "etsy",
    # account
    "ebay_account",
    "amazon_account",
    "etsy_account",
    # category
    "ebay_category",
    "amazon_category",
    "etsy_category",
    # product
    "base_product",
    "ebay_listing",
    "amazon_product",
    "etsy_listing",
    # ebay entities
    "ebay_location",
    "ebay_policy",
    "ebay_negotiation",
    # etsy entities
    "etsy_policy",
    # order
    "ebay_order",
    "amazon_order",
    "etsy_order",
    # other
    {
        "app": "sites",
        "label": "Сайты",
        "models": ({"model": "sites.Site", "label": "Сайты"},),
    },
)

# DRF settings
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated",],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser",],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
}

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ["JWT"],
}

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "user/password/reset/confirm/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "user/username/reset/confirm/{uid}/{token}",
    "ACTIVATION_URL": "user/activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": True,
    "TOKEN_MODEL": None,
    "HIDE_USERS": True,
}

CORS_ORIGIN_ALLOW_ALL = True


# Twillio
TWILIO_SERVICE_SID = env("TWILIO_SERVICE_SID")
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN")
TWILIO_CHANNEL = env("TWILIO_CHANNEL")
TWILIO_LOCALE = env("TWILIO_LOCALE")
