from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os
from config.constants import *

from src.model import Model

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

socketio = SocketIO(app)

model = Model(
    os.getenv('OFFICERS_PATH'),
    os.getenv('POLICE_SAVE'),
    os.getenv('OFFICERS_SAVE'),
    os.getenv('EVENTS_PATH'),
    MAX_CRIMES_PER_DAY,
    DUTY_DURATION,
    TODAY
)

from webapp import routes
