class NoHomeworkError(Exception):
    def __init__(self, message: str, begin_date: str, end_date: str):
        self.message = message
        self.begin_date = begin_date
        self.end_date = end_date

    def ready_message(self, setting_dw: bool) -> str:
        if setting_dw:
            return f'{self.message} (c {self.begin_date} по {self.end_date})'
        else:
            return f'{self.message} (на {self.begin_date})'
