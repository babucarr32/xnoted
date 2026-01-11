from textual.widgets import MarkdownViewer
from src.utils.database import Database


class Body(MarkdownViewer):
    def __init__(self, database: Database):
        super().__init__(show_table_of_contents=False)
        self.code_indent_guides = False
        self.storage = database

    def show_task(self, task_id: str) -> None:
        """Display the content of a specific task by its ID"""
        tasks = self.storage.load()

        if tasks:
            for task in tasks:
                if task.get("id") == task_id:
                    content = task.get("content")
                    self.document.update(content)
                    break
