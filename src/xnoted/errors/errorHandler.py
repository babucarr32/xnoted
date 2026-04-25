from typing import TypeAlias, Literal, Any, Callable
from dataclasses import dataclass
from xnoted.errors.appError import AppError
from xnoted.utils.logger import get_logger

SeverityLevel: TypeAlias = Literal["information", "warning", "error"]


@dataclass
class ErrorData:
    title: str
    content: str
    severity: SeverityLevel


class ErrorHandler:
    def __init__(self, file_name: str, error: Any, cb: Callable[[ErrorData], None]):
        logger = get_logger(__name__)

        if isinstance(error, AppError):
            logger.exception(error)
            cb(
                ErrorData(
                    title=error.title, content=error.content, severity=error.severity
                )
            )

        else:
            logger.exception(error)
            cb(
                ErrorData(
                    title="Unexpected Error", content=str(error), severity="error"
                )
            )

    def __str__(self):
        return f"[{self.severity}] {self.content}"
