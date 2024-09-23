# backend/services/speech_detector.py

import webrtcvad
import logging
import numpy as np

class SpeechDetector:
    def __init__(self, mode=3):
        self.vad = webrtcvad.Vad(mode)
        self.logger = logging.getLogger('SpeechDetector')

    def detect(self, audio_data):
        try:
            # Ensure audio_data is 16-bit PCM mono
            if audio_data.ndim > 1:
                audio_data = audio_data[:,0]
            audio_data = (audio_data * 32768).astype(np.int16).tobytes()
            # webrtcvad expects 20ms frames
            frame_duration = 30  # in ms, match your chunk duration
            sample_rate = 16000  # match your sample rate
            num_bytes_per_frame = int(sample_rate * (frame_duration / 1000.0) * 2)  # 2 bytes per sample (16-bit)
            # Process each frame
            is_speech = False
            for i in range(0, len(audio_data), num_bytes_per_frame):
                frame = audio_data[i:i + num_bytes_per_frame]
                if len(frame) == num_bytes_per_frame:
                    if self.vad.is_speech(frame, sample_rate):
                        is_speech = True
                        break
            return is_speech
        except Exception as e:
            self.logger.error(f"Speech detection failed: {e}")
            return False

