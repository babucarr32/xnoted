from typing import Any
from xnoted.errors.appError import AppError


class PasswordError(AppError):
    def __init__(self, message: str, error: Any = None):
        super().__init__(
            title="Password Error",
            error=error,
            message=message,
            severity="error",
        )
