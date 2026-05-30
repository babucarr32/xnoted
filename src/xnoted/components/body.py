from textual.widgets import MarkdownViewer
from textual.app import Timer
from xnoted.database.dataProvider import DataProvider
from textual.reactive import var
from xnoted.errors.errorHandler import ErrorHandler
from xnoted.utils.helpers import find_file
from xnoted.config.manager import ConfigHandler



class Body(MarkdownViewer):
    """Main content area for displaying README and task details."""

    _pending_task_id: var[str | None] = var(None)

    def __init__(self, data_provider: DataProvider, config_handler: ConfigHandler):
        super().__init__(show_table_of_contents=False)
        self.code_indent_guides = False
        self.data_provider = data_provider
        self._debounce_timer: Timer | None = None
        self.config_handler=config_handler

    def welcome(self) -> None:
        """Load and display README content on mount."""
        try:
            banner_path = find_file("banner.md")
            readme_path = find_file("README.md")

            content = readme_path.read_text(encoding="utf-8")
            banner = banner_path.read_text(encoding="utf-8")

            lines = content.splitlines()

            if lines:
                lines[0] = banner.strip()
            else:
                lines = [banner.strip()]

            updated_content = "\n".join(lines)

            self.document.update(updated_content)
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def show_task(self, task_id: str, debounce_ms: int = 150) -> None:
        """Display the content of a specific task by its ID with debouncing.

        Args:
            task_id: The unique identifier of the task to display
            debounce_ms: Milliseconds to wait before updating
        """
        # Cancel previous timer
        if self._debounce_timer is not None:
            self._debounce_timer.stop()

        # Set new timer
        self._debounce_timer = self.set_timer(
            debounce_ms / 1000, lambda: self._update_task(task_id)
        )

    def _update_task(self, task_id: str) -> None:
        """Internal method to actually update the task display."""
        try:
            task = self.data_provider.get_task(task_id)

            if task is None:
                self.document.update(
                    f"# Task Not Found\n\nNo task found with ID: {task_id}"
                )
                return

            if task.is_protected == 1:
                self.document.update("# Protected")
                return

            content = task.content or ""

            if not content:
                self.document.update("# Empty Task")
                return

            self.document.update(content)
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )
