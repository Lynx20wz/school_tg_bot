def get_weekday(number: int | None = None) -> str | list[str]:
    weekdays = {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье',
    }
    if number is None:
        return list(weekdays.values())
    elif number in range(1, 8):
        return weekdays[number]
    else:
        raise ValueError('Wrong number of the day of the week!')
