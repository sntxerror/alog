# backend/models/event.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)  # 'sound' or 'speech'
    label = Column(Text, nullable=False)
    confidence = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    duration = Column(Float)
    meta_info = Column(Text)
    audio_id = Column(String(100))

    def __repr__(self):
        return f"<Event(id={self.id}, type={self.event_type}, label={self.label}, confidence={self.confidence})>"

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'label': self.label,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'meta_info': self.meta_info,
            'audio_id': self.audio_id,
        }
