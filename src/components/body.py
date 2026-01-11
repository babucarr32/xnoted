from pathlib import Path
from textual.widgets import MarkdownViewer
from src.utils.database import Database


class Body(MarkdownViewer):
    """Main content area for displaying README and task details."""
    
    def __init__(self, database: Database):
        super().__init__(show_table_of_contents=False)
        self.code_indent_guides = False
        self.storage = database
    
    def welcome(self) -> None:
        """Load and display README content on mount."""
        readme_path = Path("README.md")
        
        try:
            content = readme_path.read_text(encoding="utf-8")
            self.document.update(content)
        except FileNotFoundError:
            self.document.update("# Welcome\n\nREADME.md not found.")
        except Exception as e:
            self.document.update(f"# Error\n\nFailed to load README: {e}")
    
    def show_task(self, task_id: str) -> None:
        """Display the content of a specific task by its ID.
        
        Args:
            task_id: The unique identifier of the task to display
        """
        task = self.storage.get_task(task_id)
        
        if task is None:
            self.document.update(f"# Task Not Found\n\nNo task found with ID: {task_id}")
            return
        content = task.get("content", "")
        
        if not content:
            self.document.update("# Empty Task")
            return
        
        self.document.update(content)
