from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.syncConfig import SyncConfigForm, FormData
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.keyringService import DBKeyring, Credentials

class SyncConfigModal(ModalScreen):
    def __init__(
        self,
        data_provider: DataProvider,
        task_id="",
    ):
        super().__init__(id="createTaskModal")
        self.task_id = task_id
        self.data_provider = data_provider

    TITLE = "Modal Title"
    SUB_TITLE = "Modal Title"
    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            SyncConfigForm(
                data_provider=self.data_provider,
                task_id=self.task_id,
                on_submit=self.on_submit
            ),
            id="modal-content",
        )

    def action_close(self) -> None:
        self.app.pop_screen()

    def on_submit(self, data: FormData) -> None:
        db_keyring = DBKeyring()
        db_keyring.set_credentials(Credentials(url=data.url, db_name=data.db_name))
        self.app.pop_screen()
