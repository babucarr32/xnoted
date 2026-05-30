from typing import Iterator
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.importExportProject import ImportExportProject
from xnoted.database.dataProvider import DataProvider
from xnoted.config.manager import ConfigHandler


class ImportExportProjectModal(ModalScreen):
    def __init__(self, data_provider: DataProvider, config_handler: ConfigHandler):
        super().__init__()
        self.data_provider = data_provider
        self.config_handler = config_handler


    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.cancel, action="close", description="Close modal")

    def compose(self) -> Iterator[Vertical]:
        yield Vertical(
            ImportExportProject(
                data_provider=self.data_provider,
                on_submit=lambda: self.action_close(),
                config_handler=self.config_handler,
            ),
        )

    def action_close(self) -> None:
        self.app.pop_screen()
