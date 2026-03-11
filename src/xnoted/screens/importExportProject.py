from typing import Iterator
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.importExportProject import ImportExportProject
from xnoted.database.dataProvider import DataProvider


class ImportExportProjectModal(ModalScreen):
    def __init__(
        self,
        data_provider: DataProvider,
    ):
        super().__init__()
        self.data_provider = data_provider

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> Iterator[Vertical]:
        yield Vertical(
            ImportExportProject(
                data_provider=self.data_provider,
            ),
        )

    def action_close(self) -> None:
        self.app.pop_screen()
