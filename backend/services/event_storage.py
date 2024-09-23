# backend/services/event_storage.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.event import Base, Event
from config import DATABASE_URI
import logging

class EventStorage:
    def __init__(self):
        self.logger = logging.getLogger('EventStorage')
        try:
            self.engine = create_engine(DATABASE_URI)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            self.logger.info("Database connected.")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")

    def store_event(self, event):
        session = self.Session()
        try:
            session.add(event)
            session.commit()
            self.logger.debug(f"Event stored: {event}")
        except Exception as e:
            self.logger.error(f"Failed to store event: {e}")
            session.rollback()
        finally:
            session.close()

    def get_events(self, start_time, end_time):
        session = self.Session()
        try:
            events = session.query(Event).filter(Event.timestamp.between(start_time, end_time)).all()
            return events
        except Exception as e:
            self.logger.error(f"Failed to retrieve events: {e}")
            return []
        finally:
            session.close()
