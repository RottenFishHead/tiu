from pathlib import Path
import os
import dj_database_url
import environ


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from .env into process environment for local development.
environ.Env.read_env(BASE_DIR / '.env')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("The SECRET_KEY environment variable is not set.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SERVE_MEDIA = os.environ.get('SERVE_MEDIA', 'False') == 'True'

default_hosts = ['localhost', '127.0.0.1', 'thisisus.fly.dev']
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', ','.join(default_hosts)).split(',')
    if host.strip()
]

# In production behind Fly.io, only the origin host should be trusted, not the full URL.
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'https://thisisus.fly.dev',
    ).split(',')
    if origin.strip()
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

# Only use secure cookies in production (when DEBUG=False)
SESSION_COOKIE_SECURE = not DEBUG  # Ensures cookies are sent over HTTPS only in production
SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = 'Lax'  # Protects against CSRF attacks
CSRF_COOKIE_SECURE = not DEBUG  # Also allow CSRF cookies to work on localhost

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

TIME_ZONE = 'America/Los_Angeles'

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

LOGIN_REDIRECT_URL = '/poker/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

R2_ACCOUNT_ID = os.environ.get("R2_ACCOUNT_ID")
R2_BUCKET_NAME = os.environ.get("R2_BUCKET_NAME")

AWS_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")

R2_CONFIGURED = bool(
    R2_ACCOUNT_ID
    and R2_BUCKET_NAME
    and AWS_ACCESS_KEY_ID
    and AWS_SECRET_ACCESS_KEY
)

if R2_CONFIGURED:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    AWS_STORAGE_BUCKET_NAME = R2_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = (
        f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    )
    AWS_S3_REGION_NAME = "auto"
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_DEFAULT_ACL = None
    # Keep uploads with matching filenames from replacing other posts' pictures.
    AWS_S3_FILE_OVERWRITE = False

    # Public URL used when Django generates image/file URLs
    AWS_S3_CUSTOM_DOMAIN = (
        "pub-39abad0d16ad443cad3673d95eca5df7.r2.dev"
    )
    AWS_QUERYSTRING_AUTH = False

else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {
                "location": str(MEDIA_ROOT),
                "base_url": MEDIA_URL,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

    AWS_STORAGE_BUCKET_NAME = None
    AWS_S3_ENDPOINT_URL = None
    AWS_S3_REGION_NAME = None
    AWS_S3_SIGNATURE_VERSION = None
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = None
    AWS_QUERYSTRING_AUTH = False
