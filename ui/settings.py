"""
Django settings for ui project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]
EXTERNAL_SECRET = os.environ["EXTERNAL_SECRET"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv("DEBUG", False))

# As the app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    "django_extensions",
    "raven.contrib.django.raven_compat",
    "django.contrib.sessions",
    "revproxy",
    "formtools",
    "ui",
    "enrolment",
    "company",
    "directory_constants",
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sso.middleware.SSOUserMiddleware',
]

ROOT_URLCONF = 'ui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'sso.context_processors.sso_user_processor',
                'ui.context_processors.feature_flags',
                'ui.context_processors.analytics',
            ],
        },
    },
]

WSGI_APPLICATION = 'ui.wsgi.application'


# # Database
# hard to get rid of this
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'LOCATION': 'unique-snowflake',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_HOST = os.environ.get('STATIC_HOST', '')
STATIC_URL = STATIC_HOST + '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Logging for development
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['console'],
                'level': 'ERROR',
                'propagate': True,
            },
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
else:
    # Sentry logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                          '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR',
                'class': (
                    'raven.contrib.django.raven_compat.handlers.SentryHandler'
                ),
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }


# directory-api
API_CLIENT_BASE_URL = os.environ["API_CLIENT_BASE_URL"]
API_CLIENT_KEY = os.environ["API_CLIENT_KEY"]

# directory-sso
SSO_API_CLIENT_BASE_URL = os.environ["SSO_API_CLIENT_BASE_URL"]
SSO_API_CLIENT_KEY = os.environ["SSO_API_CLIENT_KEY"]
SSO_LOGIN_URL = os.environ["SSO_LOGIN_URL"]
SSO_LOGOUT_URL = os.environ["SSO_LOGOUT_URL"]
SSO_SIGNUP_URL = os.environ["SSO_SIGNUP_URL"]
SSO_REDIRECT_FIELD_NAME = os.environ["SSO_REDIRECT_FIELD_NAME"]
SSO_SESSION_COOKIE = os.environ["SSO_SESSION_COOKIE"]

# directory-ui
SUPPLIER_CASE_STUDY_URL = os.environ['SUPPLIER_CASE_STUDY_URL']
SUPPLIER_PROFILE_LIST_URL = os.environ['SUPPLIER_PROFILE_LIST_URL']
SUPPLIER_PROFILE_URL = os.environ['SUPPLIER_PROFILE_URL']

ANALYTICS_ID = os.getenv("ANALYTICS_ID")

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Sentry
RAVEN_CONFIG = {
    "dsn": os.getenv("SENTRY_DSN"),
}

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'true') == 'true'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

VALIDATOR_MAX_LOGO_SIZE_BYTES = int(os.getenv(
    "VALIDATOR_MAX_LOGO_SIZE_BYTES", 2 * 1024 * 1024
))
VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES = int(os.getenv(
    "VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES", 2 * 1024 * 1024
))
VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES = int(os.getenv(
    "VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES", 20 * 1024 * 1024
))
VALIDATOR_ALLOWED_IMAGE_FORMATS = ('PNG', 'JPG', 'JPEG')

API_CLIENT_CLASSES = {
    'default': 'directory_api_client.client.DirectoryAPIClient',
    'unit-test': 'directory_api_client.dummy_client.DummyDirectoryAPIClient',
}
API_CLIENT_CLASS_NAME = os.getenv('API_CLIENT_CLASS_NAME', 'default')
API_CLIENT_CLASS = API_CLIENT_CLASSES[API_CLIENT_CLASS_NAME]

COMPANIES_HOUSE_API_KEY = os.environ['COMPANIES_HOUSE_API_KEY']

FEATURE_NEW_HEADER_FOOTER_ENABLED = (
    os.getenv('FEATURE_NEW_HEADER_FOOTER_ENABLED') == 'true'
)
FEATURE_UNSUBSCRIBE_VIEW_ENABLED = (
    os.getenv('FEATURE_UNSUBSCRIBE_VIEW_ENABLED') == 'true'
)

# Google tag manager
GOOGLE_TAG_MANAGER_ID = os.environ['GOOGLE_TAG_MANAGER_ID']
GOOGLE_TAG_MANAGER_ENV = os.getenv('GOOGLE_TAG_MANAGER_ENV', '')
UTM_COOKIE_DOMAIN = os.environ['UTM_COOKIE_DOMAIN']
