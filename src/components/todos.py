from textual.widgets import ListView, ListItem, Label
from src.utils.constants import ICONS
from src.components.body import Body
from src.screens.createTodo import CreateToDoModal
from src.utils.database import Database
from textual.binding import Binding
from textual.reactive import reactive


class Todos(ListView):
    def __init__(self, database=Database):
        super().__init__(id="todos")
        self.has_todo_result = True
        self.database = database

    BINDINGS = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
        Binding("e", "edit_todo", "Cursor down", show=False),
        Binding("left", "change_status('left')", "Change status", show=False),
        Binding("right", "change_status('right')", "Change status", show=False),
    ]

    status_index = reactive(2)

    def on_mount(self):
        self.load_todos()

    def load_todos(self) -> None:
        todos = self.database.load()
        self.clear()
        if todos:
            for todo in todos:
                title = todo.get("title")
                todo_id = todo.get("id")
                status = todo.get("status", 0)
                list_item = ListItem(Label(f"{ICONS[status].get('icon')} {title}"))
                list_item.todo_id = todo_id
                list_item.status = status
                self.append(list_item)
        else:
            self.append(ListItem(Label("No todos yet")))

    def refresh_todos(self):
        """Public method to refresh the todo list"""
        self.load_todos()

    def quick_search(self, text: str) -> None:
        """Public method to quick search the todo list"""
        todos = self.database.load()

        if not text:
            self.has_todo_result = True

        if not self.has_todo_result:
            return

        self.clear()

        if todos and self.has_todo_result:
            found_any = False
            for todo in todos:
                title = todo.get("title")
                if text.lower() in title.lower():
                    todo_id = todo.get("id")
                    list_item = ListItem(Label(f"● {title}"))
                    list_item.todo_id = todo_id
                    self.append(list_item)
                    found_any = True

            if not found_any:
                self.has_todo_result = False
                self.append(ListItem(Label("No matching todos")))
        else:
            self.append(ListItem(Label("No todos yet")))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and hasattr(event.item, "todo_id"):
            # Display the highlighted todo
            todo_id = event.item.todo_id
            body_widget = self.app.query_one(Body)
            body_widget.show_todo(todo_id)

    def action_edit_todo(self):
        child = self.highlighted_child

        if child and hasattr(child, "todo_id"):
            todos = self.database.load()
            todo_id = child.todo_id

            for todo in todos:
                if todo.get("id") == todo_id:
                    title = todo.get("title")
                    content = todo.get("content")
                    self.app.push_screen(
                        CreateToDoModal(
                            database=self.database,
                            title=title,
                            content=content,
                            editing=True,
                            todo_id=todo_id,
                        )
                    )
                    break

    def action_change_status(self, direction: str):
        child = self.highlighted_child
        if child is None or not hasattr(child, "todo_id"):
            return

        # Get current status for this specific item
        current_status = getattr(child, "status", 0)

        # Update status index for this item
        if direction == "right" and current_status < len(ICONS) - 1:
            new_status = current_status + 1
        elif direction == "left" and current_status > 0:
            new_status = current_status - 1
        elif direction == "left" and current_status == 0:
            new_status = len(ICONS) - 1
        else:
            new_status = 0

        # Update only the highlighted item's label
        label = child.query_one(Label)
        title = label.content.split(" ", 1)[1]
        label.update(f"{ICONS[new_status].get('icon')} {title}")
        child.status = new_status

        todos = self.database.load()
        for todo in todos:
            if todo.get("id") == child.todo_id:
                todo["status"] = new_status
                break
        self.database.update(todos)
