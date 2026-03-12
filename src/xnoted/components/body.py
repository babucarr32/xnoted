from textual.widgets import MarkdownViewer
from textual.app import Timer
from xnoted.database.dataProvider import DataProvider
from textual.reactive import var
from xnoted.utils.logger import get_logger
from xnoted.utils.helpers import find_readme

logger = get_logger(__name__)

class Body(MarkdownViewer):
    """Main content area for displaying README and task details."""
    
    _pending_task_id: var[str | None] = var(None)
    
    def __init__(self, data_provider: DataProvider):
        super().__init__(show_table_of_contents=False)
        self.code_indent_guides = False
        self.data_provider = data_provider
        self._debounce_timer: Timer | None = None

    def welcome(self) -> None:
        """Load and display README content on mount."""        
        try:
            readme_path = find_readme()
            logger.error(readme_path)
            content = readme_path.read_text(encoding="utf-8")
            self.document.update(content)
        except FileNotFoundError:
            self.document.update("# Welcome\n\nREADME.md not found.")
            logger.error(f"Welcome README.md not found. Path: {readme_path}")
        except Exception as e:
            self.document.update(f"# Error\n\nFailed to load README: {e}")
            logger.error(f"Error failed to load README: {readme_path}")
    
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
            debounce_ms / 1000,
            lambda: self._update_task(task_id)
        )
    
    def _update_task(self, task_id: str) -> None:
        """Internal method to actually update the task display."""
        task = self.data_provider.get_task(task_id)
        
        if task is None:
            self.document.update(f"# Task Not Found\n\nNo task found with ID: {task_id}")
            return

        if task.is_protected == 1:
            self.document.update("# Protected")
            return
        
        content = task.content or ''
        
        if not content:
            self.document.update("# Empty Task")
            return
        
        self.document.update(content)
