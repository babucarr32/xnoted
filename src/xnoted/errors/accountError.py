from xnoted.errors.appError import AppError


class AccountError(AppError):
    def __init__(self, message: str):
        super().__init__(
            title="Account Error",
            error=None,
            message=message,
            severity="error",
        )
