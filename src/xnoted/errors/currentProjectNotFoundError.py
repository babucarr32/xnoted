from xnoted.errors.appError import AppError


class CurrentProjectNotFoundError(AppError):
    def __init__(self):
        super().__init__(
            title="Project Error",
            error=None,
            message="No project selected. Call set_current_project() first.",
            severity="error",
        )
