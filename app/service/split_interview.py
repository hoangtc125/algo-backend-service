import random
from typing import Dict, List
from copy import deepcopy


def split_interview(appointments_dict: Dict, n_per_shift: List, auto_adjust=False):
    n_shifts = len(n_per_shift)
    schedule = [[] for _ in range(n_shifts + 1)]
    appointments_dict = dict(
        sorted(appointments_dict.items(), key=lambda item: item[1])
    )
    for id_appointment, appointment in appointments_dict.items():
        if not sum(appointment):
            continue
        target = []
        for id_shift in range(n_shifts):
            if (
                len(schedule[id_shift]) < n_per_shift[id_shift]
                and appointments_dict[id_appointment][id_shift] == 1
            ):
                target.append(id_shift)
        if not target:
            schedule[n_shifts].append(id_appointment)
        else:
            min_shift_members = {j: len(schedule[j]) for j in target}
            schedule[min(min_shift_members, key=min_shift_members.get)].append(
                id_appointment
            )
    if auto_adjust:
        schedule_more = [[] for _ in range(n_shifts)]
        for id_appointment in deepcopy(schedule[-1]):
            target = [
                id_shift
                for id_shift, is_appoint in enumerate(appointments_dict[id_appointment])
                if is_appoint == 1
            ]
            min_shift_members = {j: len(schedule_more[j]) for j in target}
            id_schedule = min(min_shift_members, key=min_shift_members.get)
            schedule[id_schedule].append(id_appointment)
            schedule[-1].remove(id_appointment)
            schedule_more[id_schedule].append(id_appointment)
    return schedule


if __name__ == "__main__":
    appointments = {i: [random.randint(0, 1) for j in range(6)] for i in range(80)}
    schedule = split_interview(appointments, [10, 10, 10, 10, 10, 10], auto_adjust=True)
    print("\n".join([f"{i}: {len(i)}" for i in schedule]))
    print([appointments[i] for i in schedule[-1]])
