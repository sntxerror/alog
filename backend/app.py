# backend/app.py

import threading
import logging
import subprocess
import os
import sys
import queue
import numpy as np

from flask import Flask, send_from_directory
from flask_restful import Api
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.event import Base
from config import DATABASE_URI, DATABASE_PATH
from logger import setup_logger
from api.endpoints import EventsAPI
from services.audio_capture import AudioCapture
from services.sound_classifier import SoundClassifier
from services.speech_recognizer import SpeechRecognizer
from services.audio_manager import AudioManager
from services.speech_detector import SpeechDetector

# Ensure the database directory exists
db_dir = os.path.dirname(DATABASE_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
    logger.info(f"Created database directory at {db_dir}")

# Set up logging
setup_logger()
logger = logging.getLogger('Alog')

db_dir = os.path.dirname(DATABASE_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)
    logger.info(f"Created database directory at {db_dir}")

# Build the frontend (if not already built)
def build_frontend():
    logger.info("Building frontend...")
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    if not os.path.exists(os.path.join(frontend_path, 'build')):
        subprocess.run(["npm", "install"], cwd=frontend_path)
        result = subprocess.run(["npm", "run", "build"], cwd=frontend_path)
        if result.returncode != 0:
            logger.error("Failed to build frontend.")
            sys.exit(1)
        else:
            logger.info("Frontend built successfully.")
    else:
        logger.info("Frontend already built.")

# Initialize the database
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)
api = Api(app)

# Register API endpoints
api.add_resource(EventsAPI, '/api/events')

# Serve the frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    # For SPA, route all unknown paths to index.html
    return send_from_directory(app.static_folder, 'index.html')

def start_services():
    audio_capture = AudioCapture(sample_rate=16000)  # Set sample_rate to 16000 Hz
    sound_classifier = SoundClassifier()
    speech_detector = SpeechDetector()
    speech_recognizer = SpeechRecognizer()
    audio_manager = AudioManager(storage_path='audio_chunks')

    audio_queue = queue.Queue()
    buffer_lock = threading.Lock()
    audio_buffer = []

    # Audio parameters
    SAMPLE_RATE = 16000
    CHUNK_DURATION = 3  # seconds
    CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

    def audio_callback(indata, frames, time_info, status):
        if status:
            logger.error(f"Audio stream status: {status}")

        with buffer_lock:
            # Flatten indata and add to buffer
            audio_buffer.extend(indata.copy().flatten())

            # Check if buffer has enough samples for CHUNK_SIZE
            if len(audio_buffer) >= CHUNK_SIZE:
                # Extract a chunk
                chunk = np.array(audio_buffer[:CHUNK_SIZE])
                del audio_buffer[:CHUNK_SIZE]

                # Enqueue the chunk for processing
                audio_queue.put(chunk)

    def process_audio():
        while True:
            chunk = audio_queue.get()
            if chunk is None:
                break  # Exit the thread

            # Store audio chunk
            audio_id = audio_manager.store_audio_chunk(chunk)

            # Classify sound in a separate thread
            threading.Thread(target=sound_classifier.classify, args=(chunk, audio_id)).start()

            # Detect speech
            if speech_detector.detect(chunk):
                # Recognize speech in a separate thread
                threading.Thread(target=speech_recognizer.recognize, args=(chunk, audio_id, 'en')).start()
            else:
                logger.debug("No speech detected.")

            # Log events to console
            logger.info(f"Processed audio chunk: {audio_id}")

            audio_queue.task_done()

    # Start the audio processing thread
    processing_thread = threading.Thread(target=process_audio, daemon=True)
    processing_thread.start()

    audio_capture.start_stream(callback=audio_callback)

    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        # Clean up on exit
        audio_queue.put(None)
        processing_thread.join()
        audio_capture.stop_stream()

if __name__ == '__main__':
    # Build the frontend
    build_frontend()

    # Start the services
    threading.Thread(target=start_services).start()

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
