from textual.widgets import ListView, ListItem, Label
from src.utils.constants import DB_PATH
from src.components.body import Body
from src.utils.storage import Storage


class Todos(ListView):
    def __init__(self):
        super().__init__()

    def on_mount(self):
        self.load_todos()

    def load_todos(self):
        storage = Storage(DB_PATH)
        todos = storage.load()

        self.clear()

        if todos:
            for todo in todos:
                title = todo.get("title")
                todo_id = todo.get("id")
                list_item = ListItem(Label(title))
                list_item.todo_id = todo_id
                self.append(list_item)
        else:
            self.append(ListItem(Label("No todos yet")))

    def refresh_todos(self):
        """Public method to refresh the todo list"""
        self.load_todos()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and hasattr(event.item, "todo_id"):
            # Display the highlighted todo
            todo_id = event.item.todo_id
            body_widget = self.app.query_one(Body)
            body_widget.show_todo(todo_id)
            self.log(todo_id, "++++++++++, content")
