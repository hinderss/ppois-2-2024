from typing import List, Optional, Tuple

from src.event import Event
from src.officer import Officer
from utils.ccolors import ccolors


def assign(officers: List[Tuple[str, Officer]],
           event: Optional[Event] = None,
           mandatory: bool = False) -> List[Officer]:
    selected_officers: List[Officer] = []
    dict_officers = {}
    counter = 1
    print(f"{ccolors.UNDERLINE}"
          f"№      Тип офицера       Имя                Звание              Опыт          Будет свободен"
          f"{ccolors.DEFAULT}")
    for status, officer in officers:
        if status == 'unavailable':
            print(ccolors.STRIKE + "{:<3} {}".format('', officer) + ccolors.DEFAULT)
        else:
            print("{:<3} {}".format(counter, officer))
            dict_officers[counter] = officer
            counter += 1

    while len(selected_officers) < len(dict_officers) and (not event or len(selected_officers) < event.slots):
        if mandatory:
            try:
                choice = int(input("Введите номер офицера: "))
            except ValueError:
                print("Повторите ввод.")
                continue
        else:
            try:
                choice = int(input("Введите номер офицера, введите -1, чтобы закончить выбор: "))
                if choice == -1:
                    break
            except ValueError:
                print("Повторите ввод.")
                continue
        if 1 <= choice <= len(dict_officers):  # and (dict_officers[choice] not in self.duty.patrol):
            if dict_officers[choice] not in selected_officers:
                selected_officers.append(dict_officers[choice])
            else:
                print("Повторите ввод.")
                continue
        else:
            print("Повторите ввод.")
            continue
    print("Офицеры отправлены")
    return selected_officers
