from textual.screen import ModalScreen
from textual.widgets import Label, ListView, ListItem
from src.utils.database import Database
from textual.binding import Binding


class Projects(ListView):
    def __init__(self, database: Database):
        super().__init__(id="projects")
        self.has_todo_result = True
        self.database = database

    BORDER_TITLE = "Projects"
    BINDINGS = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
        Binding("e", "edit_project", "Cursor down", show=False),
    ]

    def on_mount(self):
        self.load_projects()

    def load_projects(self) -> None:
        projects = self.database.load_projects()

        # self.clear()
        if projects:
            for project in projects:
                title = project.get("title")
                todo_id = project.get("id")
                list_item = ListItem(Label(f"{title}"))
                list_item.todo_id = todo_id
                self.append(list_item)
        else:
            self.append(ListItem(Label("No projects yet")))

    def on_list_view_selected(self, event: ListView.Highlighted) -> None:
        print("Selected......", event)

class SelectProjectModal(ModalScreen):
    def __init__(self, database: Database):
        self.database = database
        super().__init__(id="createToDoModal")

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self):
        yield Projects(database=self.database)

    def action_close(self):
        self.app.pop_screen()
