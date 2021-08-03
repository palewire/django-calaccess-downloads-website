import os
import dj_database_url
import django_heroku

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '8++yeqnsqgtb8=%oa0&*oa8$2o*6gh0j-+5o+0kq-uq-ycoo3@'
DEBUG = os.environ.get("DEBUG") != "false"

ALLOWED_HOSTS = []
ADMINS = (
    ('Ben Welsh', 'b@palewi.re'),
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'calaccess_raw',
    'calaccess_scraped',
    'calaccess_processed',
    'calaccess_processed_filings',
    'calaccess_processed_elections',
    'calaccess_processed_flatfiles',
    'opencivicdata.core.apps.BaseConfig',
    'opencivicdata.elections.apps.BaseConfig',
    'calaccess_website',
    'storages',
    'toolbox',
    'whitenoise.runserver_nostatic'
]

SITE_ID = 1
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = False
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'calaccess_website.context_processors.calaccess_website',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

#
# Email
#

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('email_user', 'cacivicdata@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_USE_TLS = True

#
# Archiving
#

CALACCESS_STORE_ARCHIVE = False
IA_STORAGE_ACCESS_KEY = os.getenv('IA_STORAGE_ACCESS_KEY')
IA_STORAGE_SECRET_KEY = os.getenv('IA_STORAGE_SECRET_KEY')
IA_STORAGE_COLLECTION = 'california-civic-data-coalition'
IA_STORAGE_CONTRIBUTOR = 'palewire'
IA_STORAGE_CREATOR = "California Secretary of State and California Civic Data Coalition"
IA_STORAGE_MEDIATYPE = "data"
IA_STORAGE_SUBJECT = [
    'government-data',
    'campaign-finance',
    'data',
    'money-in-politics',
    'open-data',
    'journalism'
]

#
# Databases
#

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "calaccess_website",
        "USER": "postgres",
        "HOST": "localhost",
        'PORT': '5432',
    }
}
DATABASES["default"].update(dj_database_url.config(conn_max_age=500, ssl_require=True))

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#
# Password validation
#

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

#
# Logging
#

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 0,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'INFO',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': []
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s|%(asctime)s|%(module)s|%(message)s',
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(message)s'
        },
    },
    'loggers': {
        'calaccess_raw.management': {
            'handlers': ['logfile', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'calaccess_scraped.management': {
            'handlers': ['logfile', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'calaccess_processed.management': {
            'handlers': ['logfile', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'calaccess_website.management': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'calaccess_processed_elections': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'calaccess_processed_filings': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'calaccess_processed_flatfiles': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'management_commands': {
            'handlers': ['mail_admins', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        'ia_storage': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

# Activate Django-Heroku.
django_heroku.settings(locals(), logging=False)

try:
    from .settings_local import *  # noqa
except ImportError:
    pass
