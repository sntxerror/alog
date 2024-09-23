# backend/logger.py

import logging
import os

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # File handler
    fh = logging.FileHandler('logs/app.log')
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Formatter with aligned columns
    formatter = logging.Formatter(
        '%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Suppress unnecessary logs
    logging.getLogger('pydub.converter').setLevel(logging.WARNING)
    logging.getLogger('VoskAPI').setLevel(logging.WARNING)
    logging.getLogger('absl').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    # Add handlers
    logger.addHandler(fh)
    logger.addHandler(ch)
