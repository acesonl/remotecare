# Django settings for remotecare project.
import os
import sys

DJANGO_DIR = os.path.dirname(os.path.abspath(__file__)) + '/..'
_ROOT_DIR = os.path.abspath(os.path.join(DJANGO_DIR))

DEBUG = False


ADMINS = (
    ('John', 'john@example.com'),
)
ALLOWED_HOSTS = ['*']
MANAGERS = ADMINS

# Use the XSendFile for all files in /media/ directory or subdirectories
USE_XSENDFILE = True
# nginx = 'X-Accel-Redirect', apache = 'X-Sendfile'
XSENDFILE_HEADER = 'X-Accel-Redirect'
# set this as the location in nginx or apache
XSENDFILE_LOCATION = 'xsendmedia'

# Maximum image upload size (5MB)
MAX_UPLOAD_SIZE = 5242880

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 1800

AUTH_USER_MODEL = 'account.User'

AUTHENTICATION_BACKENDS = (
    'core.backends.EmailBackend',
    # Only e-mail is allowed to be used for login.
    # 'django.contrib.auth.backends.ModelBackend',
)

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        # Or path to database file if using sqlite3.
        'NAME': 'remote_care',
        'USER': 'remote_care',                      # Not used with sqlite3.
        'PASSWORD': 'remote_care',                  # Not used with sqlite3.
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
    },

}

# URL where users will be directed if they are required to login
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Amsterdam'
DATE_FORMAT = 'j F Y'
SHORT_DATE_FORMAT = 'j b Y'
SHORT_MONTH_FORMAT = 'b Y'
SHORT_YEAR_FORMAT = 'Y'
SHORT_CUSTOM_FORMAT = '%d %B %Y'

TIME_FORMAT = 'H:i'
DATETIME_FORMAT = '%s, %s' % (DATE_FORMAT, TIME_FORMAT)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODES = ('en', 'nl')
LANGUAGE_CODE = 'nl'
LANGUAGE_BIDI = False
LOCALE_PATHS = ('%s/locale' % DJANGO_DIR,)

SITE_ID = 1

# Mollie login and Messagebird access key
MOLLIE_USERNAME = 'ExampleIncRemoteCare'
MOLLIE_PASSWORD = 'aez8eiGh'
MESSAGE_BIRD_ACCESS_KEY = 'PleaseChangeMe'

# Keys for encryption for sms authentication and password change request
MASTER_KEY = 'EiF9aizooxaquae2iV4ceing9Eir2gea3Ol6Aech1to3ke5ohl2Pheid8aeng0ei'
SMS_KEY = 'Ol6Aech1to3k'
EMAIL_KEY = 'F9aizooxaqu'
USER_KEY = 'ke5ohl2Pheid8aen'

# HMAC SEARCH keys for fields on User model
FIRSTNAME_SEARCH_KEY = 'Vohv3ugheef1'
SURNAME_SEARCH_KEY = 'Vohv3ugheef1'
USERNAME_SEARCH_KEY = 'Vohv3ugheef1'
BSN_SEARCH_KEY = '1231231231231'
HOSPITAL_NUMBER_SEARCH_KEY = '12398908123123'
EMAIL_SEARCH_KEY = 'Vohv3ugheef1'

# API encryption keys
API_ENCRYPTION_KEY = 'Vohv3ugheef1'
API_HASH_KEY = 'Vohv3ugheef1'

# Email host
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'Remote Care <noreply.remotecare@example.com>'

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
MEDIA_ROOT = os.path.join(_ROOT_DIR, 'mediafiles')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(_ROOT_DIR, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    os.path.join(_ROOT_DIR, 'staticfiles'),
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'z6ct@@hlh=ss1@op^*1x_5yvnr%a0o*ky-gjmxo%w#a0^uu%ep'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'remotecare.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'remotecare.wsgi.application'

# Project apps for Jenkins.
PROJECT_APPS = (
    'core',
    'apps.account',
    'apps.rcmessages',
    'apps.service',
    'apps.lists',
    'apps.healthperson',
    'apps.healthperson.healthprofessional',
    'apps.healthperson.patient',
    'apps.healthperson.secretariat',
    'apps.healthperson.management',
    'apps.questionnaire',
    'apps.questionnaire.default',
    'apps.questionnaire.ibd',
    'apps.questionnaire.qohc',
    'apps.questionnaire.qol',
    'apps.questionnaire.rheumatism',
    'apps.report',
    'apps.appointment',
    'apps.information',
    'apps.utils',
    'apps.audit',
)

# apps that have doc strings but are not Django apps.
EXTRA_DOC_APPS = (
    'core.encryption',
    'core.templatetags',
    'core.unittest',
)

ATOMIC_REQUESTS = True

# Installed apps
INSTALLED_APPS = (
    'core',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.account',
    'apps.rcmessages',
    'apps.service',
    'apps.lists',
    'apps.healthperson',
    'apps.healthperson.healthprofessional',
    'apps.healthperson.patient',
    'apps.healthperson.secretariat',
    'apps.healthperson.management',
    'apps.questionnaire',
    'apps.questionnaire.default',
    'apps.questionnaire.ibd',
    'apps.questionnaire.qohc',
    'apps.questionnaire.qol',
    'apps.questionnaire.rheumatism',
    'apps.report',
    'apps.appointment',
    'apps.information',
    'apps.utils',
    'apps.audit',
    'django_extensions',
    'formtools',
#    'django_jenkins',
    'pipeline',
    'rest_framework',
    'rest_framework.authtoken',
    'apps.api',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

)

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.api.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


# Replace the list below with 'default.css' for production
PIPELINE_CSS = {
    'default': {
        'source_filenames': (
            'css/cssObjects/normalize.css',
            'css/cssObjects/global.css',
            'css/cssObjects/theme.css',
            'css/cssObjects/typography.css',
            'css/cssObjects/frame.css',
            'css/cssObjects/layout.css',
            'css/cssObjects/box.css',
            'css/cssObjects/sprite.css',
            'css/cssObjects/sprite2.css',
            'css/cssObjects/ico.css',
            'css/cssObjects/list.css',
            'css/cssObjects/nav.css',
            'css/cssObjects/label.css',
            'css/cssObjects/form.css',
            'css/cssObjects/tooltip.css',
            'css/cssObjects/button.css',
            'css/cssObjects/table.css',
            'css/cssObjects/optionbar.css',
            'css/cssObjects/responsive.css',
            'css/scrollbars.css',
        ),
        'output_filename': 'css/default.css',
    },
    'default_context': {
        'source_filenames': (
            'css/jquery.ui.css',
        ),
        'output_filename': 'css/default_context.css',
    },
}

PIPELINE_JS = {
    'default': {
        'source_filenames': (
            'js/jquery.js',
            'js/jquery.tinyscrollbar.min.js',
        ),
        'output_filename': 'js/default.js',
    },
    'default_context': {
        'source_filenames': (
            'js/jquery.ui.js',
            'js/utils.js',
        ),
        'output_filename': 'js/default_context.js',
    },
}

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
    # 'core.run_csslint',
    'django_jenkins.tasks.run_sloccount'
)

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    # 'template_timings_panel.panels.TemplateTimings.TemplateTimings',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

DEBUG_TOOLBAR_CONFIG = {
    'HIDE_IN_STACKTRACES': ('threading', 'wsgiref', 'debug_toolbar'),
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

# override with dev settings if available
try:
    from remotecare.dev_settings import *
except ImportError:
    pass

# override with server settings if available
try:
    from remotecare.server_settings import *
except ImportError:
    pass


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(DJANGO_DIR, 'templates').replace(os.path.sep, '/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                "core.context_processors.datetime_format",
            ],
        },
    },
]

# Overrides for testing

# Use sqlite3 as database for testing
# Replacing with postgresql can give errors because the usage
# of ###.objects.all()[0] which does not always give the same
# object using postgresql. Also sqlite is faster.


class DisableMigrations(object):
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

if 'test' in sys.argv or 'jenkins' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase'
    }
    MOLLIE_FAKE = True
    # Store sent SMS in settings instead
    # so can be checked by tests
    SMS_STORE = []
    AUTOMATIC_TESTING = True

    # Set this to True to disable auditing during testing
    # saves approx 5 seconds.
    DISABLE_AUDITING_DURING_TEST = False
    MIGRATION_MODULES = DisableMigrations()
else:
    MOLLIE_FAKE = False  # pragma: no cover
    AUTOMATIC_TESTING = False
    DISABLE_AUDITING_DURING_TEST = False

if DEBUG:
    # Don't sent SMS or EMAIL when in DEBUG mode
    # E-mail & SMS will be printed to stdout instead
    MOLLIE_FAKE = True
    SMS_STORE = []
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # Cannot use XSendFile directive in DEBUG setting
    USE_XSENDFILE = False

if DEBUG and not AUTOMATIC_TESTING:
    INSTALLED_APPS += (
        # 'debug_toolbar',
        # 'template_timings_panel',
    )

# if not DEBUG and not AUTOMATIC_TESTING:
# List of callables that know how to import templates from various sources.
#    TEMPLATE_LOADERS = (
#        ('django.template.loaders.cached.Loader', (TEMPLATE_LOADERS)),
#    )

PIPELINE = {
    'CSS_COMPRESSOR': 'core.compressors.CSSMinCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.yuglify.YuglifyCompressor',
    'PIPELINE_ENABLED': not DEBUG,
    'STYLESHEETS': PIPELINE_CSS,
    'JAVASCRIPT': PIPELINE_JS,
}
