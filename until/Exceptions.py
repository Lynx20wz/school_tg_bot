class ExpiredToken(Exception):
    def __init__(
        self,
        message='Срок действия токена истёк! Пожалуйста введите команду /token, чтобы получить новый токен.',
    ):
        super().__init__(message)


class NoToken(Exception):
    def __init__(
        self,
        message='У вас отсутствует токен! Пожалуйста введите команду /token, чтобы получить его!',
    ):
        super().__init__(message)


class ServerError(Exception):
    def __init__(
        self, message='Произошла ошибка при получении информации. Повторите попытку позже.'
    ):
        super().__init__(message)
