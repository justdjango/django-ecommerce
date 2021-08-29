# flake8: noqa
from .settings import *

DEBUG = True
ALLOWED_HOSTS += ['*']
WSGI_APPLICATION = 'market.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('APP_DB_NAME'),
        'USER': '{}@{}'.format(os.getenv('POSTGRES_ADMIN_USER'), os.getenv('POSTGRES_SERVER_NAME')),
        'PASSWORD': os.getenv('POSTGRES_ADMIN_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'},
    }
}

STATICFILES_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_ACCOUNT_NAME = os.getenv('AZ_STORAGE_ACCOUNT_NAME')
AZURE_CONTAINER = os.getenv('AZ_STORAGE_CONTAINER')
AZURE_ACCOUNT_KEY = os.getenv('AZ_STORAGE_KEY')
