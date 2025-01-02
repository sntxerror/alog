# backend/config.py

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'events.db')
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

# Logging configuration
# You can override these with environment variables
class LogConfig:
    # Default logging level - can be overridden by LOG_LEVEL env var
    # Valid values: DEBUG, EVENT, SPEECH, INFO, WARNING, ERROR, CRITICAL
    DEFAULT_LOG_LEVEL = os.getenv('LOG_LEVEL', 'EVENT')
    
    # Define custom log level values (between INFO and WARNING)
    SPEECH_LEVEL = 25
    EVENT_LEVEL = 26
    
    # List of enabled log levels - can be overridden by ENABLED_LOG_LEVELS env var
    # Format: comma-separated list of levels, e.g. "EVENT,SPEECH,ERROR"
    DEFAULT_ENABLED_LEVELS = os.getenv('ENABLED_LOG_LEVELS', 'EVENT,SPEECH,ERROR')
    
    @classmethod
    def get_enabled_levels(cls):
        """Convert enabled_levels string to a set of logging levels"""
        enabled = cls.DEFAULT_ENABLED_LEVELS.split(',')
        levels = set()
        
        # Map level names to their numeric values
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'EVENT': cls.EVENT_LEVEL,
            'SPEECH': cls.SPEECH_LEVEL,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        for level in enabled:
            level = level.strip().upper()
            if level in level_map:
                levels.add(level_map[level])
                
        return levels