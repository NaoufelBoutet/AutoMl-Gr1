"""
Django settings for autoML2 project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=r'C:\Users\kaeli\OneDrive\Documents\GitHub\AutoMl-Gr1\.env')

MONGO_CONFIG = {
    "DB_NAME": os.getenv("MONGO_DB_NAME"),
    "HOST": os.getenv("MONGO_HOST"),
    "PORT": int(os.getenv("MONGO_PORT",27017)),
    "USER": os.getenv("MONGO_USER",None),
    "PASSWORD": os.getenv("MONGO_PASS",None)
}

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-a-^5&m6n^e)hkz^bu7^^t&y2fl#9y_rs((vz_)7el6trg*1fwu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auth_user',
    'main'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'autoML.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'autoML.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("NAME_PG"),
        'USER': os.getenv("USER_PG"),
        'PASSWORD': os.getenv("PASSWORD_PG"),
        'HOST': os.getenv("HOST_PG"),
        'PORT': int(os.getenv("PORT_PG", 5432)),
        'OPTIONS': {
            'options': '-c search_path=auth_schema',
        },
    },
    'users_data': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("NAME_PG"),
        'USER': os.getenv("USER_PG"),
        'PASSWORD': os.getenv("PASSWORD_PG"),
        'HOST': os.getenv("HOST_PG"),
        'PORT': int(os.getenv("PORT_PG", 5432)),
        'OPTIONS': {
            'options': '-c search_path=user_data_schema',
        },
    },
}

DATABASE_ROUTERS = ['autoML.db_router.AuthRouter']


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # ou autre backend de session
SESSION_COOKIE_SECURE = True  # Assurez-vous que les cookies de session sont sécurisés en HTTPS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True