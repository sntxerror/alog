# backend/services/audio_capture.py

import sounddevice as sd
import logging

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
SECONDS_PER_CHUNK = 2  # Each audio chunk duration
CHUNK_SIZE = int(SAMPLE_RATE * SECONDS_PER_CHUNK)  # Calculate chunk size

class AudioCapture:
    def __init__(self, sample_rate=SAMPLE_RATE, channels=CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self.logger = logging.getLogger('AudioCapture')

    def start_stream(self, callback):
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback,
            blocksize=CHUNK_SIZE  # Set blocksize to match your chunk size
        )
        self.stream.start()
        self.logger.info("Audio stream started.")

    def stop_stream(self):
        try:
            self.stream.stop()
            self.stream.close()
            self.logger.info("Audio stream stopped.")
        except Exception as e:
            self.logger.error(f"Failed to stop audio stream: {e}")