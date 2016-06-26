"""
Settings overrides for running unittests
"""
from __future__ import absolute_import
from .settings import *  # NOQA

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'calaccess_website',
    },
}
