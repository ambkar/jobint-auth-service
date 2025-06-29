class AuthError(Exception):
    """Базовая ошибка auth-сервиса."""


class DuplicateEmailError(AuthError):
    """E-mail уже зарегистрирован."""


class InvalidCredentials(AuthError):
    """Неверная пара логин/пароль."""
