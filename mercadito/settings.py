from pathlib import Path
import os
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================================
# SECURITY
# ========================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key-change-in-production-12345')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, 'localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CSRF
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']

# ========================================
# APPLICATIONS
# ========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party
    'rest_framework',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    
    # Local apps
    'users',
    'products',
    'cart',
    'orders',
    'reviews',
    'scraping',
    'payments',
    'core',
]

# ========================================
# MIDDLEWARE
# ========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# ========================================
# URLS Y WSGI
# ========================================
# 🔴 CAMBIAR "mercadito" por el nombre REAL de tu carpeta principal
ROOT_URLCONF = 'mercadito.urls'
WSGI_APPLICATION = 'mercadito.wsgi.application'

# ========================================
# TEMPLATES
# ========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_count',
            ],
        },
    },
]

# ========================================
# DATABASE
# ========================================
if os.environ.get('DATABASE_URL'):
    # Producción (Render con PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Desarrollo local (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ========================================
# PASSWORD VALIDATION
# ========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================================
# INTERNATIONALIZATION
# ========================================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'

# ========================================
# STATIC FILES
# ========================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Whitenoise para servir archivos estáticos
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========================================
# MEDIA FILES
# ========================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========================================
# CUSTOM USER
# ========================================
AUTH_USER_MODEL = 'users.CustomUser'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================================
# LOGIN/LOGOUT
# ========================================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# ========================================
# REST FRAMEWORK
# ========================================
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

# ========================================
# SESSION
# ========================================
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_SAVE_EVERY_REQUEST = True

# ========================================
# ALLAUTH
# ========================================
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'
ACCOUNT_SIGNUP_REDIRECT_URL = 'home'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'github': {
        'SCOPE': ['user', 'email'],
    }
}

# ========================================
# LOGGING (solo para debug en Render)
# ========================================
if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }