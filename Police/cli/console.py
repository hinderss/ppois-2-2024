from typing import List, Tuple

from cli import model
from cli.assign import assign
from src.model import PrepareDutyData
from src.officer import Officer, Detective, PatrolOfficer
from src.police import Police
from utils.ccolors import ccolors


def index():
    police: Police = model.police
    if police is None:
        welcome()
    else:
        print(f'Отлично, {police.chief_officer}!')
        user_choice = input("Нажмите Y - чтобы начать смену, любую другую кнопку - чтобы выйти: ")
        if user_choice.upper() == "Y":
            prepare()
        print("Вы вышли.")


def welcome():
    officers = model.officer_list
    print("Добро пожаловать в ""Модель полиции"".")
    city = input("Для того, чтобы продолжить введите город, где находится ваш полицейский участок: ")
    print(f"У вас в участке работает {len(officers)} полицейских.")
    name = input("Введите ваше имя, чтобы знать как к вам обращаться: ")
    model.create_police(city, name)
    index()


def prepare():
    police: Police = model.police
    if police is None:
        index()
    else:
        data: PrepareDutyData = model.pre_prepare_duty()

        cases = data.cases

        for status, investigation in cases:
            if status == 'report':
                print(investigation.report)
            else:
                print(f"Дело:\n{investigation}\n...ещё расследуется.\n")

        print(f"{ccolors.WARNING}Вы начинаете смену {data.date}{ccolors.DEFAULT}\nсегодня офицеры нужны для:")
        print(data.patrol_event)

        print(f"Назначьте офицеров на патруль:")
        patrol = assign(
            [(status, officer)
             for status, officer in data.patrol_list
             if isinstance(officer, PatrolOfficer)],
            data.patrol_event,
            True
        )

        print(f"Назначьте детективов сегодня:")
        detective = assign(
            [(status, officer)
             for status, officer in data.detective_list
             if isinstance(officer, Detective)]
        )

        print(f"Назначьте офицеров, которые будут отвечать на вызовы:")
        public_security_list: List[Tuple[str, Officer]] = [(status, officer)
                                                           for status, officer in data.patrol_list
                                                           if officer not in patrol]
        public_security = assign(public_security_list)
        model.prepare_duty(patrol, detective, public_security)
        call()


def call():
    police: Police = model.police
    if police is None:
        return welcome()
    elif model.duty is None:
        return prepare()

    t = model.duty.timenow.strftime("%d.%m.%Y %H:%M")
    print(f"\n{ccolors.WARNING}Доброе утро, {police.chief_officer}."
          f"Ваша смена началась. {ccolors.DEFAULT} {t}")

    print('Ожидание вызовов...')
    event = model.request_call()
    while event is not None:
        print(f"\n{ccolors.GREEN}Текущее время: {model.duty.timenow}\nСчёт: {model.duty.score}{ccolors.DEFAULT}")
        print(event)
        if event.type == 'call':
            officers = model.duty.public_security_team
        else:
            officers = model.duty.detective

        officers_dicts = []
        for officer in officers:
            if officer.unavailable_until > model.duty.timenow:
                x = ('unavailable', officer)
            else:
                x = ('available', officer)
            officers_dicts.append(x)

        assigned = assign(officers_dicts, event)
        if len(assigned) == 0:
            print("Вызов проигнорирован.\n")
        _ = model.handle_event(assigned)
        print('Ожидание вызовов...')
        event = model.request_call()
    result()


def result():
    police: Police = model.police
    if police is None:
        welcome()
    elif model.duty is None:
        prepare()
    else:
        print(f"{ccolors.FAIL}Смена закончена. Счёт: {model.duty.score}{ccolors.DEFAULT}")
        print('Можно приступать к следующей смене!')
        user_choice = input("Нажмите Y - чтобы начать смену, любую другую кнопку - чтобы выйти: ")
        if user_choice.upper() == "Y":
            prepare()
        print("Вы вышли.")


if __name__ == '__main__':
    index()
