# backend/services/sound_classifier.py

import tensorflow as tf
import numpy as np
import logging
from models.event import Event
from services.event_storage import EventStorage
from datetime import datetime
import os
import csv

class SoundClassifier:
    def __init__(self):
        self.logger = logging.getLogger('SoundClassifier')
        try:
            # Load the YAMNet model from the SavedModel directory
            model_path = os.path.join('models', 'yamnet')
            self.model = tf.saved_model.load(model_path)
            # Access the serving signature
            self.infer = self.model.signatures['serving_default']

            # Load class names from yamnet_class_map.csv
            class_map_path = os.path.join('models', 'yamnet', 'assets', 'yamnet_class_map.csv')
            with open(class_map_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip the header
                self.class_names = [row[2] for row in reader]  # 'display_name' is the third column

            self.event_storage = EventStorage()
            self.logger.info("YAMNet model loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load YAMNet model: {e}")

    def classify(self, audio_data, audio_id):
        try:
            # Ensure audio_data is a 1-D float32 array
            if audio_data.ndim > 1:
                audio_data = np.mean(audio_data, axis=1)
            audio_data = audio_data.astype(np.float32)

            # Normalize audio data
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val

            # Convert to tensor without adding batch dimension
            audio_tensor = tf.convert_to_tensor(audio_data, dtype=tf.float32)

            # Run inference using the serving signature
            outputs = self.infer(input_waveform=audio_tensor)
            scores = outputs['output_0'].numpy()

            mean_scores = np.mean(scores, axis=0)
            top_indices = np.argsort(mean_scores)[::-1][:5]
            timestamp = datetime.utcnow()

            # Group similar events
            event_group = []
            for idx in top_indices:
                label = self.class_names[idx]
                confidence = float(mean_scores[idx])

                event = Event(
                    event_type='sound',
                    label=label,
                    confidence=confidence,
                    timestamp=timestamp,
                    audio_id=audio_id
                )
                self.event_storage.store_event(event)
                event_group.append(event)

            # Log grouped events
            self.logger.info(f"Sound Events Grouped: {[str(event) for event in event_group]}")

        except Exception as e:
            self.logger.error(f"Sound classification failed: {e}")
