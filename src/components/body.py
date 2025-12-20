from textual.widgets import MarkdownViewer
from src.utils.constants import DB_PATH
from src.utils.storage import Storage


class Body(MarkdownViewer):
    def __init__(self):
        super().__init__(show_table_of_contents=False)
        self.code_indent_guides = False

    def show_todo(self, todo_id: str) -> None:
        """Display the content of a specific todo by its ID"""
        storage = Storage(DB_PATH)
        todos = storage.load()

        if todos:
            for todo in todos:
                if todo.get("id") == todo_id:
                    content = todo.get("content")
                    self.document.update(content)
                    break
