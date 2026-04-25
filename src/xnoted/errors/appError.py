from typing import TypeAlias, Literal, Any

SeverityLevel: TypeAlias = Literal["information", "warning", "error"]


class AppError(Exception):
    def __init__(self, title: str, error: Any, message: str, severity: SeverityLevel):
        self.title = title
        self.content = message
        self.severity = severity
        self.error = error
        super().__init__(message)

    def __str__(self):
        return f"[{self.severity}] {self.content}"
