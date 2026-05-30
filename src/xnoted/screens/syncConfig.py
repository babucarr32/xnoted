from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.syncConfig import SyncConfigForm, FormData
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import SYNC_CONFIG_ID
from xnoted.utils.keyringService import DBKeyring, Credentials
from xnoted.config.manager import ConfigHandler


class SyncConfigModal(ModalScreen):
    def __init__(
        self,
        config_handler: ConfigHandler,
        data_provider: DataProvider,
        task_id="",
    ):
        super().__init__(id=SYNC_CONFIG_ID)
        self.task_id = task_id
        self.data_provider = data_provider
        self.config_handler = config_handler

    TITLE = "Modal Title"
    SUB_TITLE = "Modal Title"

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.cancel, action="close", description="Close modal")

    def compose(self) -> ComposeResult:
        yield Vertical(
            SyncConfigForm(
                data_provider=self.data_provider,
                task_id=self.task_id,
                on_submit=self.on_submit,
                config_handler=self.config_handler,
            ),
        )

    def action_close(self) -> None:
        self.app.pop_screen()

    def on_submit(self, data: FormData) -> None:
        db_keyring = DBKeyring()
        db_keyring.set_credentials(Credentials(url=data.url, db_name=data.db_name))
        self.app.pop_screen()
