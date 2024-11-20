# backend/services/audio_manager.py

import os
import uuid
import logging
import time
from threading import Thread
from pydub import AudioSegment
import numpy as np

class AudioManager:
    def __init__(self, storage_path='audio_chunks'):
        self.storage_path = storage_path
        self.logger = logging.getLogger('AudioManager')
        os.makedirs(self.storage_path, exist_ok=True)
        self.cleanup_thread = Thread(target=self.cleanup_old_files)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()

    def store_audio_chunk(self, audio_data):
        try:
            audio_id = str(uuid.uuid4())
            filepath = os.path.join(self.storage_path, f"{audio_id}.mp3")
            # Ensure audio_data is int16
            if audio_data.dtype != np.int16:
                audio_data = (audio_data * 32767).astype(np.int16)
            audio_segment = AudioSegment(
                audio_data.tobytes(),
                frame_rate=16000,
                sample_width=2,  # 2 bytes per sample
                channels=1
            )
            audio_segment.export(filepath, format="mp3", bitrate="64k")
            self.logger.debug(f"Audio chunk stored: {filepath}")
            return audio_id
        except Exception as e:
            self.logger.error(f"Failed to store audio chunk: {e}")
            return None

    def get_audio_chunk(self, audio_id):
        filepath = os.path.join(self.storage_path, f"{audio_id}.mp3")
        if os.path.exists(filepath):
            return filepath
        else:
            self.logger.error(f"Audio chunk not found: {audio_id}")
            return None

    def cleanup_old_files(self):
        while True:
            now = time.time()
            for filename in os.listdir(self.storage_path):
                filepath = os.path.join(self.storage_path, filename)
                if os.path.isfile(filepath):
                    creation_time = os.path.getctime(filepath)
                    if now - creation_time > 24 * 3600:
                        os.remove(filepath)
                        self.logger.info(f"Deleted old audio chunk: {filepath}")
            time.sleep(3600)  # Check every hour
