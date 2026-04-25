from typing import Any
from xnoted.errors.appError import AppError


class DatabaseError(AppError):
    def __init__(self, message: str, error: Any):
        super().__init__(
            title="Database Error",
            error=error,
            message=message,
            severity="error",
        )
