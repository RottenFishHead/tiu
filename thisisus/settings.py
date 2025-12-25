from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from BASE_DIR
load_dotenv(BASE_DIR / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("The SECRET_KEY environment variable is not set.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['thisisus.fly.dev', 'localhost', '127.0.0.1', 'https://thisisus.fly.dev']


# Application definition

INSTALLED_APPS = [
    'expenses.apps.ExpensesConfig',
    'income.apps.IncomeConfig',
    'john.apps.JohnConfig',
    'poker.apps.PokerConfig',
    'blog.apps.BlogConfig',
    'hands.apps.HandsConfig',
    'todo.apps.TodoConfig',
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'django.contrib.flatpages',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'celery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'thisisus.urls'
CSRF_TRUSTED_ORIGINS = ['https://thisisus.fly.dev/']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'thisisus.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),  # Load DATABASE_URL from .env
        conn_max_age=600,  # Optional: Keep database connections open for 600 seconds
        conn_health_checks=True,  # Optional: Enable connection health checks
    )
}

CSRF_TRUSTED_ORIGINS = ["https://thisisus.fly.dev",  # full URL with https
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Set the session cookie to persist (e.g., 2 weeks)
SESSION_COOKIE_AGE = 15552000  # 6 months in seconds

# Allow session cookies to persist even after the browser is closed
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_COOKIE_SECURE = True  # Ensures cookies are sent over HTTPS only
SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = 'Lax'  # Protects against CSRF attacks

STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media" 
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

X_FRAME_OPTIONS = 'SAMEORIGIN'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"