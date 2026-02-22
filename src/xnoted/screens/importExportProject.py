from typing import Iterator
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.importExportProject import ImportExportProject
from xnoted.utils.database import Database

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

    def compose(self) -> Iterator[Vertical]:
        yield Vertical(
            ImportExportProject(
                database=self.database,
            ),
        )

    def action_close(self) -> None:
        self.app.pop_screen()
