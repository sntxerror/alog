# backend/logger.py

import logging
import os
from datetime import datetime
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform color support
colorama.init()

class CustomLogLevels:
    """Define custom log levels as class attributes for better organization"""
    SPEECH = 25  # Between INFO and WARNING
    EVENT = 26   # Between INFO and WARNING

class SoundEventLogger(logging.Logger):
    """
    Custom logger class that adds support for sound events and speech recognition.
    This class extends the standard Logger to add methods specifically for our audio processing needs.
    """
    
    def speech(self, message, language="En", *args, **kwargs):
        """
        Log a speech recognition event with the detected language.
        
        Args:
            message (str): The transcribed speech text
            language (str): The language code (e.g., "En", "Ru")
        """
        if self.isEnabledFor(CustomLogLevels.SPEECH):
            # Create extra dict with our custom fields
            extra = {
                'language': language,
                'sound_category': None,
                'confidence': None
            }
            # Pass extra fields through kwargs to avoid duplication
            self._log(CustomLogLevels.SPEECH, message, args, extra=extra)

    def event(self, message, category=None, confidence=None, *args, **kwargs):
        """
        Log a sound event with its category and confidence level.
        
        Args:
            message (str): The detected sound event
            category (str): The category of the sound (e.g., "Human Sounds")
            confidence (float): Confidence level of the detection (0-1)
        """
        if self.isEnabledFor(CustomLogLevels.EVENT):
            # Create extra dict with our custom fields
            extra = {
                'language': None,
                'sound_category': category,
                'confidence': confidence
            }
            # Pass extra fields through kwargs to avoid duplication
            self._log(CustomLogLevels.EVENT, message, args, extra=extra)

class ColorFormatter(logging.Formatter):
    """
    Custom formatter that creates aligned columns for different types of log messages.
    Each field gets a fixed width to ensure consistent alignment regardless of content length.
    """
    
    # Define column widths
    WIDTHS = {
        'date': 10,        # YYYY-MM-DD
        'time': 10,         # HH:MM:SS
        'level': 15,        # Longest level name
        'confidence': 5,  # Confidence value
        'message': 35,    # Main message/transcription
        'category': 50,    # Event category
        'event': 25,      # Event name
    }
    
    # Color schemes for different log levels
    FORMATS = {
        logging.DEBUG: Fore.CYAN + Style.DIM,
        logging.INFO: Fore.WHITE,
        CustomLogLevels.SPEECH: Fore.GREEN,
        CustomLogLevels.EVENT: Fore.YELLOW,
        logging.WARNING: Fore.YELLOW + Style.BRIGHT,
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + Style.BRIGHT
    }

    def truncate_or_pad(self, text, width, align='left'):
        """
        Helper method to ensure text fits in its column.
        Truncates long text with ellipsis and pads short text with spaces.
        """
        if len(text) > width:
            # Leave room for ellipsis
            return text[:width-3] + '...'
        if align == 'right':
            return text.rjust(width)
        return text.ljust(width)

    def format(self, record):
        """
        Format the log record with aligned columns based on log type.
        Creates different layouts for system/speech logs versus event logs.
        """
        # Format timestamp components
        timestamp = datetime.fromtimestamp(record.created)
        date_str = self.truncate_or_pad(
            timestamp.strftime('%Y-%m-%d'), 
            self.WIDTHS['date']
        )
        time_str = self.truncate_or_pad(
            timestamp.strftime('%H:%M:%S'), 
            self.WIDTHS['time']
        )
        
        # Format level with color
        level_color = self.FORMATS.get(record.levelno, '')
        level_str = self.truncate_or_pad(
            f"{level_color}{record.levelname}{Style.RESET_ALL}",
            self.WIDTHS['level']
        )

        # Handle different log types
        if record.levelno == CustomLogLevels.EVENT:
            # Event log format
            message = record.getMessage()
            category = getattr(record, 'sound_category', '')
            confidence = getattr(record, 'confidence', 0)
            
            # Format each field
            event_str = self.truncate_or_pad(message, self.WIDTHS['event'])
            category_str = self.truncate_or_pad(
                category if category else '', 
                self.WIDTHS['category']
            )
            confidence_str = self.truncate_or_pad(
                f"{confidence:.1%}" if confidence is not None else '',
                self.WIDTHS['confidence'],
                align='right'
            )
            
            # Combine all fields
            log_fmt = (
                f"{Fore.BLUE}{date_str} | {time_str}{Style.RESET_ALL} | "
                f"{level_str} | "
                f"{category_str} | "
                f"{event_str} |"
                f"{confidence_str} | "
            )
        else:
            # System/Speech log format
            message = record.getMessage()
            if record.levelno == CustomLogLevels.SPEECH:
                lang = getattr(record, 'language', '')
                message = f"[{lang}] {message}" if lang else message
            
            # Format message field
            message_str = self.truncate_or_pad(message, self.WIDTHS['message'])
            
            # Combine fields for system/speech logs
            log_fmt = (
                f"{Fore.BLUE}{date_str} | {time_str}{Style.RESET_ALL} | "
                f"{level_str} | "
                f"{message_str}"
            )

        return log_fmt

class LevelFilter(logging.Filter):
    """
    A filter that only allows specified log levels to pass through.
    Works with both standard and custom log levels.
    """
    def __init__(self, enabled_levels=None):
        super().__init__()
        # If no levels specified, default to EVENT, SPEECH, and ERROR
        self.enabled_levels = enabled_levels or {
            CustomLogLevels.EVENT,
            CustomLogLevels.SPEECH,
            logging.ERROR,
        }
    
    def filter(self, record):
        return record.levelno in self.enabled_levels

    @classmethod
    def from_env_string(cls, level_string=None):
        """
        Create a filter from an environment variable string.
        Example: "EVENT,SPEECH,ERROR,DEBUG"
        """
        if not level_string:
            return cls()
            
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'EVENT': CustomLogLevels.EVENT,
            'SPEECH': CustomLogLevels.SPEECH,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        enabled_levels = set()
        for level in level_string.split(','):
            level = level.strip().upper()
            if level in level_map:
                enabled_levels.add(level_map[level])
                
        return cls(enabled_levels)

def setup_logger():
    """
    Set up the logging system with custom formatting and handlers.
    Now supports configurable log levels through ENABLED_LOG_LEVELS environment variable.
    """
    # Register custom log levels
    logging.addLevelName(CustomLogLevels.SPEECH, 'SPEECH')
    logging.addLevelName(CustomLogLevels.EVENT, 'EVENT')
    
    # Set our custom logger class as the default
    logging.setLoggerClass(SoundEventLogger)
    
    # Create and configure the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Catch all logs, filtering happens at handler level

    # Create level filter from environment variable
    level_filter = LevelFilter.from_env_string(os.getenv('ENABLED_LOG_LEVELS'))

    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)

    # Configure file handler for persistent logging - keeps all levels
    fh = logging.FileHandler('logs/app.log')
    fh.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%Y-%m-%d | %H:%M:%S'
    )
    fh.setFormatter(file_formatter)

    # Configure console handler with color formatting and level filtering
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColorFormatter())
    ch.addFilter(level_filter)  # Add the level filter only to console output

    # Suppress verbose logs from external libraries
    for logger_name in ['pydub.converter', 'VoskAPI', 'absl', 'werkzeug']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Remove any existing handlers to prevent duplication
    logger.handlers.clear()
    
    # Add both handlers to the root logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # Log the enabled levels for confirmation
    logger.info(f"Logger initialized with levels: {os.getenv('ENABLED_LOG_LEVELS', 'EVENT,SPEECH,ERROR')} (default)")

    return logger