# backend/api/endpoints.py

from flask import request
from flask_restful import Resource
from services.event_storage import EventStorage
from marshmallow import Schema, fields
from dateutil.parser import isoparse  # Import isoparse
import logging

class EventSchema(Schema):
    id = fields.Int()
    event_type = fields.Str()
    label = fields.Str()
    confidence = fields.Float()
    timestamp = fields.DateTime()
    duration = fields.Float()
    meta_info = fields.Str()
    audio_id = fields.Str()


class EventsAPI(Resource):
    def get(self):
        logger = logging.getLogger('EventsAPI')
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        if not start_time_str or not end_time_str:
            return {'error': 'start_time and end_time parameters are required'}, 400

        try:
            start_time = isoparse(start_time_str)
            end_time = isoparse(end_time_str)
        except Exception as e:
            logger.error(f"Date parsing error: {e}")
            return {'error': 'Invalid date format'}, 400

        try:
            event_storage = EventStorage()
            events = event_storage.get_events(start_time, end_time)
            events_dict = [event.to_dict() for event in events]
            return events_dict, 200
        except Exception as e:
            logger.error(f"Failed to retrieve events: {e}")
            return {'error': 'Failed to retrieve events'}, 500