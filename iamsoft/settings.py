# Django settings for iamsoft project.
from ambiente import ambiente

AMBIENTE=ambiente

DEBUG = (not ambiente.productivo)
TEMPLATE_DEBUG = DEBUG
CRISPY_FAIL_SILENTLY = not DEBUG

CRISPY_TEMPLATE_PACK = 'bootstrap'

ADMINS = ambiente.admins

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': ambiente.db.name,                      # Or path to database file if using sqlite3.
        'USER': ambiente.db.user,                      # Not used with sqlite3.
        'PASSWORD': ambiente.db.password,                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

#DATABASE_ROUTERS = ['direccion.routers.CitiesLightRouter']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Sao_Paulo'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pt-BR'
#LANGUAGE_CODE = 'es-AR'

gettext = lambda s: s

LANGUAGES = (
  ('pt-br', gettext('Portugues')),
  ('es', gettext('Spanish')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ambiente.project_directory+'uploads'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/uploads/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ambiente.project_directory+'collectedstatic'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #ambiente.project_directory+'iamsoft/static',
    #ambiente.project_directory+'direccion/static',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@7002fz*)2boj%6sl1b#(asc@crqm8e5j0l_#%+sgoo%e6)o$)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'iamsoft.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'iamsoft.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ambiente.project_directory+'templates',
)

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'imagekit',
    'crispy_forms',
    #'south', 
    #'cities_light',
    #'smart_selects',
    # Aplicaciones de la agencia
    #'direccion',
    #'telefono',
    'iampacks.cross.estatico',
    'iampacks.cross.correo',
    'iampacks.cross.usuario',
    'iampacks.cross.idioma',
    'iampacks.cross.mercadopago',
    'iampacks.cross.crontab',
    'iampacks.cross.zonomi',
    'iampacks.cross.install',
    'home',
    'iamcast',
)

if not ambiente.productivo:
  if ambiente.app_in_dev is not None:
    INSTALLED_APPS+=ambiente.app_in_dev

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters':{
      'verbose':{
        'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
      },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            #'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'debug_file':{
            'level': 'DEBUG',
            'filename': ambiente.log_file,
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'iamcast':{
            'handlers': ['debug_file'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

EMAIL_USE_TLS = ambiente.email.use_tls
EMAIL_HOST = ambiente.email.host
EMAIL_HOST_USER = ambiente.email.user
EMAIL_HOST_PASSWORD = ambiente.email.password
EMAIL_PORT = ambiente.email.port

TEMPLATE_CONTEXT_PROCESSORS=(
  "django.contrib.auth.context_processors.auth",
  "django.core.context_processors.debug",
  "django.core.context_processors.i18n",
  "django.core.context_processors.media",
  "django.core.context_processors.static",
  "django.core.context_processors.tz",
  "django.contrib.messages.context_processors.messages",
# La linea que sigue se agrego por uni-form
  'django.core.context_processors.request',
  'home.context_processors.ambiente',
  #'agencia.context_processors.add_thumbnails_urls',
  #'agencia.context_processors.add_agencia',
)

LOCALE_PATHS=(ambiente.project_directory+'locale',)

#CITIES_LIGHT_CITY_SOURCES = ['http://download.geonames.org/export/dump/BR.zip','http://download.geonames.org/export/dump/AR.zip']
#CITIES_LIGHT_CITY_SOURCES = ['http://download.geonames.org/export/dump/cities5000.zip']

DIAS_PRUEBA_IAMCAST=7
