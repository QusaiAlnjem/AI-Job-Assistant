import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = []

SECRET_KEY = os.environ.get('SECRET_KEY')

LLM_API_KEY = os.environ.get('LLM_API_KEY')
ENDPOINT = "https://qusaihub7213425342.services.ai.azure.com/openai/v1/"
MODEL_NAME = "DeepSeek-V3.2"

AUTH_USER_MODEL = 'users.CustomUser'

DEBUG = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',

    # Local apps
    'users',
    'resumes',
    'jobs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Allow cookies/auth headers to be sent
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR, 'frontend'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
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
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/assets/'

# Where the static folder is
STATICFILES_DIRS = [BASE_DIR / 'frontend/assets']

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/min',  # Strict limit for login attempts
        'user': '100/day'
    }
}