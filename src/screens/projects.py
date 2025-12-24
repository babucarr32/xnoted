from textual.screen import ModalScreen
from textual.widgets import Label, ListView, ListItem
from src.utils.database import Database
from textual.binding import Binding
from src.utils.helpers import slugify
from src.screens.createProject import CreateProjectModal
from src.utils.constants import PROJECTS_ID, SELECT_PROJECT_ID


class Projects(ListView):
    def __init__(self, database: Database):
        super().__init__(id=PROJECTS_ID)
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

        if projects:
            for project in projects:
                title = project.get("title")
                project_id = project.get("id")
                list_item = ListItem(Label(f"{title}"))
                list_item.project_id = project_id
                list_item.project_name = slugify(title)
                self.append(list_item)
        else:
            self.append(ListItem(Label("No projects yet")))

    def on_list_view_selected(self, event: ListView.Highlighted) -> None:
        project_name = event.item.project_name
        self.database.project_name = project_name
        todos_widget = self.app.query_one("#todos")
        todos_widget.refresh_todos()

    def action_edit_project(self):
        child: ListItem = self.highlighted_child

        if child and hasattr(child, "project_id"):
            project_id = child.project_id
            project = self.database.get_project(project_id)
            self.app.push_screen(
                CreateProjectModal(
                    database=self.database,
                    title=project["title"],
                    description=project["description"],
                    editing=True,
                    project_id = project_id,
                    project_type=project["type"],
                )
            )


class SelectProjectModal(ModalScreen):
    def __init__(self, database: Database):
        self.database = database
        super().__init__()

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self):
        yield Projects(database=self.database)

    def action_close(self):
        self.app.pop_screen()
