import pickle
import datetime
import time
from dataclasses import dataclass
import random
from typing import Optional, List, Tuple

from src.event import Event
from src.officer import Officer, PatrolOfficer, Detective
from src.police import Police
from utils.utils import Loader, EventGenerator


@dataclass
class PrepareDutyData:
    date: str
    cases: list
    patrol_event: Event
    patrol_list: List[Tuple[str, Officer]]
    detective_list: List[Tuple[str, Officer]]


class Model:
    def __init__(self,
                 officers_path: str,
                 police_save: str,
                 officers_save: str,
                 events_path: str,
                 max_crimes_per_day: int,
                 duty_duration: int,
                 today: datetime.datetime
                 ):
        self.officer_list: Optional[List[Officer]] = None
        self.__police_save: str = police_save
        self.__officers_save: str = officers_save
        self.__time = today
        self.__duty_duration = duty_duration
        self.__police: Optional[Police] = None
        try:
            with open(officers_save, 'rb') as f:
                self.officer_list: List[Officer] = pickle.load(f)
        except FileNotFoundError:
            self.officer_list: List[Officer] = Loader.load_officers(officers_path, self.__time)
        EventGenerator(events_path, max_crimes_per_day)

    @property
    def duty(self):
        return self.__police.duty

    @property
    def score(self):
        if self.__police is not None:
            return self.__police.duty.score
        return 0

    @score.setter
    def score(self, value):
        self.__police.duty.score = value

    @property
    def police(self):
        if self.__police is None:
            try:
                with open(self.__police_save, 'rb') as f:
                    police: Police = pickle.load(f)
                    self.__police = police
                    return police
            except FileNotFoundError:
                return None
        return self.__police

    def create_police(self, city: str, chief_officer: str):
        police: Police = Police(city, chief_officer, self.officer_list, self.__time)
        with open(self.__police_save, 'wb') as f:
            pickle.dump(police, f)
        self.__police = police
        return police

    def pre_prepare_duty(self):
        if self.__police is not None:
            self.__police.create_duty()
            cases = self.__police.case_analysis()
            public_security_event = self.__police.get_public_security_event()

            patrol_list: List[Tuple[str, Officer]] = []
            for i in self.officer_list:
                if isinstance(i, PatrolOfficer):
                    if i.unavailable_until > self.duty.timenow:
                        patrol_list.append(('unavailable', i))
                    else:
                        patrol_list.append(('available', i))

            detective_list: List[Tuple[str, Officer]] = []
            for i in self.officer_list:
                if isinstance(i, Detective):
                    if i.unavailable_until > self.duty.timenow:
                        detective_list.append(('unavailable', i))
                    else:
                        detective_list.append(('available', i))

            return PrepareDutyData(date=self.duty.timenow.strftime("%d.%m.%Y %H:%M"),
                                   cases=cases,
                                   patrol_event=public_security_event,
                                   patrol_list=patrol_list,
                                   detective_list=detective_list
                                   )
        return None

    def prepare_duty(self, patrol_list, detective_list, public_security_list):
        self.__police.duty.patrol = patrol_list
        self.__police.duty.detective = detective_list
        self.__police.duty.public_security_team = public_security_list
        self.__police.duty.duty_end = self.duty.timenow + datetime.timedelta(hours=self.__duty_duration)

    def request_call(self) -> Optional[Event]:
        time.sleep(random.randint(3, 5))
        if self.duty.timenow <= self.__police.duty.duty_end:
            event = self.__police.get_call()
            return event
        else:
            self.__police.duty_start = self.__police.duty_start + datetime.timedelta(days=1)
            with open(self.__police_save, 'wb') as f:
                pickle.dump(self.__police, f)
            with open(self.__officers_save, 'wb') as f:
                pickle.dump(self.officer_list, f)
            return None

    def handle_event(self, officers):
        return self.__police.handle_event(officers)

