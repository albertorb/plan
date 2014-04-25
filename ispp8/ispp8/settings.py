"""
Django settings for ispp8 project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))




ADMINS = (
     ('Alberto', 'arincon1992@gmail.com'),
)

MANAGERS = ADMINS


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open('../secretdjangokey.txt') as f:# # # # # # # # # # # #
    SECRET_KEY = f.read().strip()       # # Production # # # # #
                                        # # # # # # # # # # # # #
# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True #Development
DEBUG = False # Production


TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [
    'plan.ispp8.com' # Production
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'plan',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

PASSWORD_HASHERS = (

    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

ROOT_URLCONF = 'ispp8.urls'

WSGI_APPLICATION = 'ispp8.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

with open('../secretdjangodatabase.txt') as f:# # # # # # # # # # # #
    DATABASE_KEY = f.read().strip()       # # Production # # # # #
                                        # # # # # # # # # # # # #
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '../djangodatabase.cnf',
        },
    }
}



# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'es-es'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

SITE_ID = 1

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://127.0.0.1:8000/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
#STATIC_ROOT = '' # Development
STATIC_ROOT = '/var/www/plan.issp8.com/static/' # Production


# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, "static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

ROOT_URLCONF = 'ispp8.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	os.path.join(BASE_DIR, "templates"),
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# $$ Usage $$
# import the logging library
#import logging

# Get an instance of a logger
#logger = logging.getLogger(__name__)

#def my_view(request, arg1, arg):
#    ...
#    if bad_mojo:
        # Log an error message
#        logger.error('Something went wrong!')

#    $ $ $ $ $ $ $ $__example-code__ $ $ $ $ $ $ $ $ $ $

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Security options
CSRF_COOKIE_SECURE = True #Production # Set this to True to avoid transmitting the CSRF cookie over HTTP accidentally.
SESSION_COOKIE_SECURE = True # Production # Set this to True to avoid transmitting the session cookie over HTTP accidentally.
    # About security using python
        #Python Options
        #It’s strongly recommended that you invoke the Python process running your Django application using the -R option or with the
        # PYTHONHASHSEED environment variable set to random.
        #These options help protect your site from denial-of-service (DoS) attacks triggered by carefully crafted inputs.
        # Such an attack can drastically increase CPU usage by causing worst-case performance when creating dict instances.
        # See oCERT advisory #2011-003 for more information.


# Optimization of performance options
# CONN_MAX_AGE = 15 #seconds to close database connection # Production #Enabling persistent database connections can result in a nice
                                                                        #speed-up when connecting to the database accounts for a significant
                                                                        # part of the request processing time.
                                    #This helps a lot on virtualized hosts with limited network performance.
# TEMPLATE_LOADERS = django.template.loaders.filesystem.Loader # Production # Enabling the cached template loader often improves
                                                                            # performance drastically, as it avoids compiling each template
                                                                            # every time it needs to be rendered. See the template loaders
                                                                            # docs for more information.


