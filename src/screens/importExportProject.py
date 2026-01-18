from textual.containers import Vertical
from textual.screen import ModalScreen
from src.components.importExportProject import ImportExportProject
from src.utils.database import Database
from src.utils.constants import (
    PROJECT_MODAL_CONTENT,
)


class ImportExportProjectModal(ModalScreen):
    def __init__(
        self,
        database: Database,
    ):
        super().__init__()
        self.database = database

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self):
        yield Vertical(
            ImportExportProject(
                database=self.database,
            ),
        )

    def action_close(self):
        self.app.pop_screen()
