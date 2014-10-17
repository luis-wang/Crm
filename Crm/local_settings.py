#coding:utf8
from settings import *


DEBUG = True
#MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'crm',
        'USER':     'root',
        'PASSWORD': 'syst3m',
        'HOST':     '127.0.0.1',
        'PORT':     '3306',
    },
    #cord db
    'cord_db': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME' :    'Cord',
        'USER' :    'root',
        'PASSWORD': 'syst3m',
        'HOST' :    '127.0.0.1',
        'PORT' :    '3306',
    },
    #New peony db
    'peony_db': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME' :    'peony_crm',
        'USER' :    'root',
        'PASSWORD': 'syst3m',
        'HOST' :    '127.0.0.1',
        'PORT' :    '3306',
    },
}

DATABASE_ROUTERS = ['cord.cord_router.CordRouter',
                    'peony.peony_router.PeonyRouter', ]


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
        },
    }
}


INTERNAL_IPS = ('127.0.0.1', )

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCERT_REDIRECT': False,
    'SHOW_TEMPLATE_CONTEXT': True,
}

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP


TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

STATIC_URL = '/static/'
STATIC_ROOT = '/home/deploy/tmp/crm_static/'