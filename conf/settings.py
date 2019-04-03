'''
Django settings for ui project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
'''

import os

from directory_components.constants import IP_RETRIEVER_NAME_GOV_UK
import directory_healthcheck.backends
import environ

env = environ.Env()
env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(PROJECT_ROOT)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', False)

# As the app is running behind a host-based router supplied by Heroku or other
# PaaS, we can open ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']

APPEND_SLASH = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django_extensions',
    'raven.contrib.django.raven_compat',
    'django.contrib.sessions',
    'revproxy',
    'formtools',
    'corsheaders',
    'enrolment',
    'company',
    'core',
    'directory_constants',
    'directory_healthcheck',
    'directory_components',
]

MIDDLEWARE_CLASSES = [
    'directory_components.middleware.MaintenanceModeMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.PrefixUrlMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sso.middleware.SSOUserMiddleware',
    'directory_components.middleware.NoCacheMiddlware',
]

FEATURE_URL_PREFIX_ENABLED = env.str('FEATURE_URL_PREFIX_ENABLED', False)
URL_PREFIX_DOMAIN = env.str('URL_PREFIX_DOMAIN', '')
if FEATURE_URL_PREFIX_ENABLED:
    ROOT_URLCONF = 'conf.urls_prefixed'
else:
    ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'directory_components.context_processors.sso_processor',
                'directory_components.context_processors.urls_processor',
                ('directory_components.context_processors.'
                 'header_footer_processor'),
                'directory_components.context_processors.feature_flags',
                'directory_components.context_processors.analytics',
                'directory_components.context_processors.cookie_notice',
            ],
        },
    },
]

WSGI_APPLICATION = 'conf.wsgi.application'

VCAP_SERVICES = env.json('VCAP_SERVICES', {})

if 'redis' in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']
else:
    REDIS_URL = env.str('REDIS_URL', '')

if REDIS_URL:
    cache = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': "django_redis.client.DefaultClient",
        }
    }
else:
    cache = {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }


CACHES = {
    'default': cache,
    'api_fallback': cache,
}


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# Static files served with Whitenoise and AWS Cloudfront
# http://whitenoise.evans.io/en/stable/django.html#instructions-for-amazon-cloudfront
# http://whitenoise.evans.io/en/stable/django.html#restricting-cloudfront-to-static-files
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_HOST = env.str('STATIC_HOST', '')
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
DIRECTORY_API_CLIENT_BASE_URL = env.str(
    'DIRECTORY_API_CLIENT_BASE_URL'
)
DIRECTORY_API_CLIENT_API_KEY = env.str(
    'DIRECTORY_API_CLIENT_API_KEY'
)
DIRECTORY_API_CLIENT_SENDER_ID = env.str(
    'DIRECTORY_API_CLIENT_SENDER_ID', 'directory'
)
DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT = env.str(
    'DIRECTORY_API_CLIENT_DEFAULT_TIMEOUT', 15
)

# directory clients
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 30 days


# Companies House
COMPANIES_HOUSE_API_KEY = env.str('COMPANIES_HOUSE_API_KEY')
COMPANIES_HOUSE_CLIENT_ID = env.str('COMPANIES_HOUSE_CLIENT_ID', '')
COMPANIES_HOUSE_CLIENT_SECRET = env.str('COMPANIES_HOUSE_CLIENT_SECRET', '')
COMPANIES_HOUSE_CALLBACK_DOMAIN = env.str(
    'COMPANIES_HOUSE_CALLBACK_DOMAIN',
    'https://find-a-buyer.export.great.gov.uk'
)

# directory-companies-house-search
DIRECTORY_CH_SEARCH_CLIENT_BASE_URL = env.str(
    'DIRECTORY_CH_SEARCH_CLIENT_BASE_URL'
)
DIRECTORY_CH_SEARCH_CLIENT_API_KEY = env.str(
    'DIRECTORY_CH_SEARCH_CLIENT_API_KEY'
)
DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID = env.str(
    'DIRECTORY_CH_SEARCH_CLIENT_SENDER_ID', 'directory'
)
DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT = env.int(
    'DIRECTORY_CH_SEARCH_CLIENT_DEFAULT_TIMEOUT', 5
)

# directory-sso-proxy
DIRECTORY_SSO_API_CLIENT_BASE_URL = env.str(
    'DIRECTORY_SSO_API_CLIENT_BASE_URL'
)
DIRECTORY_SSO_API_CLIENT_API_KEY = env.str(
    'DIRECTORY_SSO_API_CLIENT_API_KEY'
)
DIRECTORY_SSO_API_CLIENT_SENDER_ID = env.str(
    'DIRECTORY_SSO_API_CLIENT_SENDER_ID', 'directory'
)
DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT = env.int(
    'DIRECTORY_SSO_API_CLIENT_DEFAULT_TIMEOUT', 5
)
SSO_PROXY_LOGIN_URL = env.str('SSO_PROXY_LOGIN_URL')
SSO_PROXY_LOGOUT_URL = env.str('SSO_PROXY_LOGOUT_URL')
SSO_PROXY_SIGNUP_URL = env.str('SSO_PROXY_SIGNUP_URL')
SSO_PROFILE_URL = env.str('SSO_PROFILE_URL')
SSO_PROXY_REDIRECT_FIELD_NAME = env.str('SSO_PROXY_REDIRECT_FIELD_NAME')
SSO_SESSION_COOKIE = env.str('SSO_SESSION_COOKIE')

# directory-ui-supplier
SUPPLIER_CASE_STUDY_URL = env.str('SUPPLIER_CASE_STUDY_URL')
SUPPLIER_PROFILE_LIST_URL = env.str('SUPPLIER_PROFILE_LIST_URL')
SUPPLIER_PROFILE_URL = env.str('SUPPLIER_PROFILE_URL')
SUPPLIER_SEARCH_URL = env.str('SUPPLIER_SEARCH_URL')

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', True)
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', '16070400')
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# HEADER/FOOTER URLS
DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC = env.str(
    'DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC', ''
)
DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES = env.str(
    'DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES', ''
)
DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS = env.str(
    'DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS', ''
)
DIRECTORY_CONSTANTS_URL_EVENTS = env.str(
    'DIRECTORY_CONSTANTS_URL_EVENTS', ''
)
DIRECTORY_CONSTANTS_URL_INVEST = env.str('DIRECTORY_CONSTANTS_URL_INVEST', '')
DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER = env.str(
    'DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER', ''
)
DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON = env.str(
    'DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON', ''
)
DIRECTORY_CONSTANTS_URL_FIND_A_BUYER = env.str(
    'DIRECTORY_CONSTANTS_URL_FIND_A_BUYER', ''
)
DIRECTORY_CONSTANTS_URL_SSO_PROFILE = env.str(
    'DIRECTORY_CONSTANTS_URL_SSO_PROFILE', ''
)

PRIVACY_COOKIE_DOMAIN = env.str('PRIVACY_COOKIE_DOMAIN')

# Sentry
RAVEN_CONFIG = {
    'dsn': env.str('SENTRY_DSN', ''),
}

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', True)
SESSION_COOKIE_NAME = env.str('SESSION_COOKIE_NAME', 'buyer_sessionid')
CSRF_COOKIE_SECURE = True

# parity with nginx config for maximum request body
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

VALIDATOR_MAX_LOGO_SIZE_BYTES = env.int(
    'VALIDATOR_MAX_LOGO_SIZE_BYTES', 2 * 1024 * 1024
)
VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES = env.int(
    'VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES', 2 * 1024 * 1024
)
VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES = env.int(
    'VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES', 20 * 1024 * 1024
)
VALIDATOR_ALLOWED_IMAGE_FORMATS = ('PNG', 'JPG', 'JPEG')

# Google tag manager
GOOGLE_TAG_MANAGER_ID = env.str('GOOGLE_TAG_MANAGER_ID')
GOOGLE_TAG_MANAGER_ENV = env.str('GOOGLE_TAG_MANAGER_ENV', '')
UTM_COOKIE_DOMAIN = env.str('UTM_COOKIE_DOMAIN')

DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET = env.str(
    'DIRECTORY_EXTERNAL_API_SIGNATURE_SECRET'
)

HEADER_FOOTER_CSS_ACTIVE_CLASSES = {'fab': True}

# CORS
CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', False)
CORS_ORIGIN_WHITELIST = env.list('CORS_ORIGIN_WHITELIST', default=[])

# Feature flags
FEATURE_FLAGS = {
    'EXPORT_JOURNEY_ON': env.bool('FEATURE_EXPORT_JOURNEY_ENABLED', True),
    'INTERNAL_CH_ON': env.bool('FEATURE_USE_INTERNAL_CH_ENABLED', False),
    # used by directory-components
    'MAINTENANCE_MODE_ON': env.bool('FEATURE_MAINTENANCE_MODE_ENABLED', False),
    # used by directory-components
    'DIRECTORY_API_ON': env.bool('EXPOSE_DIRECTORY_API', False),
    'NEW_ACCOUNT_JOURNEY_ON': env.bool(
        'FEATURE_NEW_ACCOUNT_JOURNEY_ENABLED', False
    ),
    'NEW_ACCOUNT_EDIT_ON': env.bool('FEATURE_NEW_ACCOUNT_EDIT_ENABLED', False),
    'NEW_HEADER_FOOTER_ON': env.bool(
        'FEATURE_NEW_HEADER_FOOTER_ENABLED', False
    ),
    'HEADER_SEARCH_ON': env.bool('FEATURE_HEADER_SEARCH_ENABLED', False)
}

# healthcheck
DIRECTORY_HEALTHCHECK_TOKEN = env.str('HEALTH_CHECK_TOKEN')
DIRECTORY_HEALTHCHECK_BACKENDS = [
    directory_healthcheck.backends.APIBackend,
    directory_healthcheck.backends.SingleSignOnBackend,
]

# Internal CH
INTERNAL_CH_BASE_URL = env.str('INTERNAL_CH_BASE_URL', '')
INTERNAL_CH_API_KEY = env.str('INTERNAL_CH_API_KEY', '')
