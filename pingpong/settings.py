"""
Django settings for pingpong project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@kz6l=vvy!)8ym(je)g@=22fhf@rq(^aj@*1@1jj^yt3o*i+4k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = not os.environ.get('PRODUCTION', False)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []
INTERNAL_IPS = ('127.0.0.1',)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'south',
    'sekizai',

    'pingpong',
    'pingpong.signup',
    'pingpong.bracket',
    'pingpong.slideshow',
    'pingpong.dashboard',
    'pingpong.printing',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",

    "sekizai.context_processors.sekizai",
    "pingpong.context_processors.login_url_with_redirect",
)

ROOT_URLCONF = 'pingpong.urls'

WSGI_APPLICATION = 'pingpong.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'sl-si'

TIME_ZONE = 'Europe/Ljubljana'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Project settings

PRINT_DIRECTORY = os.path.join(BASE_DIR, "print")

# Heroku settings
# Parse database configuration from $DATABASE_URL
import dj_database_url

DATABASES['default'] = dj_database_url.config(default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite'))

# Honor the 'X-Forwarded-Proto' header for request.is_secure()

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if DEBUG:
    INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
