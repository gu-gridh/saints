"""
Django settings for saints project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from .common import *
from .common import INSTALLED_APPS

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

INTERNAL_IPS = [
    "127.0.0.1",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_LOCAL_NAME'),
        'USER': os.getenv('DB_LOCAL_USER'),
        'PASSWORD': os.getenv('DB_LOCAL_PASS'),
        'HOST': os.getenv('HOST'),
        'PORT': os.getenv('PORT'),
    }
}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 2500
