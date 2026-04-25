from xnoted.errors.appError import AppError


class EncryptionError(AppError):
    def __init__(self, message: str):
        super().__init__(
            title="Encryption Error",
            error=None,
            message=message,
            severity="error",
        )
