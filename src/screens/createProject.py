from textual.containers import Vertical
from textual.screen import ModalScreen
from src.components.createProjectForm import CreateProjectForm
from src.utils.database import Database

class CreateProjectModal(ModalScreen):
    def __init__(self, database: Database):
        self.database = database
        super().__init__(id="createToDoModal")

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self):
        yield Vertical(
            CreateProjectForm(database=self.database),
            id="project-modal-content",
        )

    def action_close(self):
        self.app.pop_screen()
