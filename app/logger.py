import logging
from logging.config import dictConfig
from queue import Queue

log_queue = Queue()
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'text': {
            'format': '%(asctime)s [%(levelname)s]:\n%(message)s\n'
        }
    },
    'handlers': {
        'print': {
            'formatter': 'text',
            'class': 'logging.StreamHandler',
            'stream': "ext://sys.stdout"
        }

    },
    'loggers': {
        'geo_preprocessing': {
            'handlers': ['print'],
            'level': 'DEBUG' if logging.DEBUG else 'INFO',
            'propagate': False,
        }
    },
}

dictConfig(LOG_CONFIG)
logger = logging.getLogger('geo_preprocessing')
