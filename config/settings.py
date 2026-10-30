"""
Django settings for config project.
"""

from pathlib import Path

# Root folder of the project (the folder that contains manage.py).
# Used to build paths like BASE_DIR / 'db.sqlite3'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY: keep your real secret key here (the one startproject generated).
# Never share it or commit it to a public repo.
SECRET_KEY = 'django-insecure-_$@(@8k1&jnk^rqvazz3a@1o#&9^(b#u!$24ej65by7w0%f8!('

# DEBUG shows detailed error pages. Fine for development, must be False in production.
DEBUG = True

# Domains allowed to serve the site. Empty is fine while DEBUG = True.
ALLOWED_HOSTS = []


# ---------------------------------------------------------------
# Applications
# ---------------------------------------------------------------
INSTALLED_APPS = [
    # Built-in Django apps
    'django.contrib.admin',          # the /admin/ site
    'django.contrib.auth',           # users, permissions, login
    'django.contrib.contenttypes',   # lets models reference other models generically
    'django.contrib.sessions',       # keeps users logged in between requests
    'django.contrib.messages',       # one-time flash messages ("Booking confirmed!")
    'django.contrib.staticfiles',    # serves CSS/JS/images

    # Our apps
    'accounts',                      # custom User model with roles
]

# Middleware = code that runs on every request/response, in this order.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',                 # protects forms from CSRF attacks
    'django.contrib.auth.middleware.AuthenticationMiddleware',   # attaches request.user
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# The main urls.py file Django starts routing from.
ROOT_URLCONF = 'config.urls'

# Template (HTML) settings.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],          # project-wide template folders (we'll add one later)
        'APP_DIRS': True,    # also look for templates/ folders inside each app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',          # gives templates `request`
                'django.contrib.auth.context_processors.auth',         # gives templates `user`
                'django.contrib.messages.context_processors.messages', # gives templates `messages`
            ],
        },
    },
]

# Entry point used by production web servers.
WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------
# Database: SQLite for development (a single db.sqlite3 file)
# ---------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------------------------------
# Password rules applied when users register or change passwords
# ---------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},  # not too similar to username/email
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},            # at least 8 characters
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},           # not a common password
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},          # not only digits
]


# ---------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------
LANGUAGE_CODE = 'en-us'

# Time zone Django uses for display and for converting dates.
# We'll revisit this when we build appointment slots.
TIME_ZONE = 'UTC'

USE_I18N = True

# Store datetimes as timezone-aware values. Important for appointments.
USE_TZ = True


# ---------------------------------------------------------------
# Static files (CSS, JavaScript, images)
# ---------------------------------------------------------------
STATIC_URL = 'static/'


# ---------------------------------------------------------------
# Email
# Console backend prints emails in the terminal instead of sending them.
# Perfect for testing reminders in development.
# ---------------------------------------------------------------
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}


# ---------------------------------------------------------------
# Custom settings (ours)
# ---------------------------------------------------------------
# Tell Django to use our User model (accounts/models.py) instead of the
# built-in one. Format is "app_label.ModelName".
# This must be set BEFORE the first migrate.
AUTH_USER_MODEL = "accounts.User"