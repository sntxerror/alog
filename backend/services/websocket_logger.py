# backend/services/websocket_logger.py

import logging
import queue
import threading
from flask_sock import Sock
from datetime import datetime
import colorama
from colorama import Fore, Style
from logger import CustomLogLevels  # Import your custom log levels

class WebSocketHandler(logging.Handler):
    """
    A logging handler that forwards logs to WebSocket clients.
    Think of this as a bridge between your logging system and the web browser.
    """
    def __init__(self):
        super().__init__()
        self.clients = set()
        self.lock = threading.Lock()
        colorama.init()
        # Set logging level to capture everything
        self.setLevel(logging.DEBUG)
    
    def emit(self, record):
        """
        This method is called whenever a log needs to be processed.
        It's like a mail carrier that delivers your log messages to their destination.
        """
        try:
            # Format the log message using the same styling as your ColorFormatter
            category_str = ""
            confidence_str = ""
            lang_str = ""

            # Preserve the extra fields from your custom logger
            if hasattr(record, 'sound_category'):
                category_str = f" | {record.sound_category}"
            if hasattr(record, 'confidence'):
                confidence_str = f" | {record.confidence:.2%}" if record.confidence is not None else ""
            if hasattr(record, 'language'):
                lang_str = f" {record.language}"

            # Get the level color like your ColorFormatter does
            FORMATS = {
                logging.DEBUG: Fore.CYAN + Style.DIM,
                logging.INFO: Fore.WHITE,
                CustomLogLevels.SPEECH: Fore.GREEN,
                CustomLogLevels.EVENT: Fore.YELLOW,
                logging.WARNING: Fore.YELLOW + Style.BRIGHT,
                logging.ERROR: Fore.RED + Style.BRIGHT,
                logging.CRITICAL: Fore.RED + Style.BRIGHT + Style.BRIGHT
            }

            # Format the message with consistent styling
            timestamp = datetime.fromtimestamp(record.created)
            log_msg = (
                f"{Fore.BLUE}{timestamp.strftime('%Y-%m-%d | %H:%M:%S')}{Style.RESET_ALL} | "
                f"{FORMATS.get(record.levelno, '')}{record.levelname:7}{Style.RESET_ALL} |"
                f"{lang_str}{category_str} {record.getMessage()}{confidence_str}"
            )

            # Send the formatted message to all connected clients
            with self.lock:
                clients = self.clients.copy()
                for client_queue in clients:
                    try:
                        client_queue.put_nowait(log_msg)
                    except queue.Full:
                        self.clients.remove(client_queue)
                        
        except Exception as e:
            # If something goes wrong, print it to stderr (will show in your console)
            import sys
            print(f"Error in WebSocketHandler: {e}", file=sys.stderr)

    def add_client(self, client_queue):
        """Register a new web browser to receive logs."""
        with self.lock:
            self.clients.add(client_queue)
            # Send a test message to confirm logging is working
            client_queue.put_nowait(f"{Fore.GREEN}Logging system connected successfully{Style.RESET_ALL}")

    def remove_client(self, client_queue):
        """Remove a web browser when it disconnects."""
        with self.lock:
            self.clients.discard(client_queue)

def setup_websocket_logging(app, logger):
    """
    Sets up the WebSocket connection and integrates it with your logging system.
    This is like building the bridge between your backend and frontend.
    """
    sock = Sock(app)
    
    # Create and configure the WebSocket handler
    ws_handler = WebSocketHandler()
    
    # This is crucial - add the handler to your logger
    logger.addHandler(ws_handler)
    
    @sock.route('/ws/logs')
    def logs(ws):
        """Handles each WebSocket connection from a browser."""
        client_queue = queue.Queue(maxsize=100)
        ws_handler.add_client(client_queue)
        
        try:
            while True:
                try:
                    # Wait for new log messages
                    message = client_queue.get(timeout=30)
                    ws.send(message)
                except queue.Empty:
                    # Send an empty message to keep the connection alive
                    ws.send('')
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            ws_handler.remove_client(client_queue)