from dotenv import load_dotenv
import os
from src.model import Model
from config.constants import *

load_dotenv()
model = Model(
    os.getenv('OFFICERS_PATH'),
    os.getenv('POLICE_SAVE'),
    os.getenv('OFFICERS_SAVE'),
    os.getenv('EVENTS_PATH'),
    MAX_CRIMES_PER_DAY,
    DUTY_DURATION,
    TODAY
)
