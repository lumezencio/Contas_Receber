# config/settings.py

import os
from pathlib import Path
from decouple import config

# --- Configurações Principais ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configurações de Segurança (lidas do arquivo .env) ---
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')


# --- Definição de Aplicações ---
LOCAL_APPS = ['financeiro', 'theme']
THIRD_PARTY_APPS = ['tailwind']
DJANGO_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
]
INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS


# --- Middlewares ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# --- Configurações de URL e WSGI ---
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# --- Templates ---
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


# --- Banco de Dados ---
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}


# --- Validação de Senhas ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- Internacionalização ---
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# --- Arquivos Estáticos ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']


# --- Configurações Padrão e de Terceiros ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ["127.0.0.1"]


# =============================================================================
# SEÇÃO DE AUTENTICAÇÃO
# =============================================================================
LOGIN_URL = 'login'
# CORREÇÃO: Após o login, o usuário será levado para o dashboard em seu novo endereço.
LOGIN_REDIRECT_URL = '/dashboard/'