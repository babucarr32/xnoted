from xnoted.errors.appError import AppError


class DecryptionError(AppError):
    def __init__(self, message: str):
        super().__init__(
            title="Decryption Error",
            error=None,
            message=message,
            severity="error",
        )
