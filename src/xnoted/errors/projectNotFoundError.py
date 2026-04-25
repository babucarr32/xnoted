from xnoted.errors.appError import AppError


class ProjectNotFoundError(AppError):
    def __init__(self, project_id: str):
        super().__init__(
            title="Project Error",
            error=None,
            message=f"Project with id {project_id} not found",
            severity="error",
        )
        self.project_id = project_id
