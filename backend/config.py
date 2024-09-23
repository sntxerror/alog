# backend/config.py

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'events.db')
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'