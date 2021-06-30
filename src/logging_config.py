import logging.config

LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)-12s %(levelname)-8s %(name)-8s %(message)s',
            'datefmt': '%d-%m'
        },
        'complete': {
            'format': '%(asctime)-12s %(levelname)-8s %(module)-8s %(name)-8s %(message)s',
            'datefmt': '%d-%m %H:%M'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': logging.INFO,
            'stream': 'ext://sys.stdout'

        },
        'filewritter': {
            'class': 'logging.FileHandler',
            'filename': 'ydl.log',
            'mode': 'w',
            'formatter': 'complete',
            'level': logging.DEBUG,
        }
    },
}
