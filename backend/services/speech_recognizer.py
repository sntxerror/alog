# backend/services/speech_recognizer.py

from vosk import Model, KaldiRecognizer
import logging
from services.event_storage import EventStorage
from models.event import Event
from datetime import datetime
import numpy as np
import json
import os

class SpeechRecognizer:
    def __init__(self):
        self.logger = logging.getLogger('SpeechRecognizer')
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Use absolute paths
            self.models = {
                'en': Model('/home/khadas/alog/models/vosk/en'),
                'ru': Model('/home/khadas/alog/models/vosk/ru')
            }
            self.event_storage = EventStorage()
            self.logger.info("Vosk models loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load Vosk models: {e}")

    def recognize(self, audio_data, audio_id, language='en'):
        try:
            # Preprocess audio_data
            if audio_data.ndim > 1:
                audio_data = np.mean(audio_data, axis=1)
            audio_data = (audio_data * 32768).astype(np.int16)

            # Select the language model
            model = self.models.get(language, self.models['en'])
            rec = KaldiRecognizer(model, 16000)
            rec.AcceptWaveform(audio_data.tobytes())
            result = rec.Result()
            text = json.loads(result).get('text', '')

            timestamp = datetime.utcnow()
            event = Event(
                event_type='speech',
                label=text.strip(),
                confidence=None,
                timestamp=timestamp,
                audio_id=audio_id
            )
            self.event_storage.store_event(event)
            self.logger.info(f"Speech Event: {event}")
        except Exception as e:
            self.logger.error(f"Speech recognition failed: {e}")
