import uuid
from textual.containers import Container
from textual.widgets import Input
from textual.app import ComposeResult
from src.utils.database import Database

PROJECT_TITLE_ID = "project-title"
PROJECT_CONTENT_ID = "project-content"

class InputContainer(Input):
    BORDER_TITLE = "Project Title"
    
    def __init__(self):
        super().__init__(id=PROJECT_TITLE_ID)

class CreateProjectForm(Container):
    def __init__(self, database: Database, title="", editing=False):
        super().__init__()
        self.database = database
        self.title = title
        self.editing = title

    BINDINGS = [
        ("ctrl+s", "submit", "Toggle dark mode"),
    ]

    def on_mount(self):
        input_widget = self.query_one(f"#{PROJECT_TITLE_ID}")
        input_widget.value = self.title

    def compose(self) -> ComposeResult:
        yield InputContainer()

    def handle_save_new(self) -> None:
        title = self.query_one(f"#{PROJECT_TITLE_ID}").value

        # Only title is required
        if title:
            data = {
                "id": str(uuid.uuid4()),
                "title": title,
            }

            self.database.save_project(data)

    def handle_edit(self) -> None:
        updated_title = self.query_one(f"#{PROJECT_TITLE_ID}").value

        projects = self.database.load_projects()
        for project in projects:
            if project.get("id") == self.project_id:
                project["title"] = updated_title
                break

        self.database.update(projects)

    def action_submit(self) -> None:
        if self.editing:
            self.handle_edit()
        else:
            self.handle_save_new()
