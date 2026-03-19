from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.sidebar import Form
from xnoted.database.dataProvider import DataProvider


class CreateTaskModal(ModalScreen):
    def __init__(
        self,
        data_provider: DataProvider,
        editing=False,
        task_id="",
    ):
        super().__init__(id="createTaskModal")
        self.editing = editing
        self.task_id = task_id
        self.data_provider = data_provider

    TITLE = "Modal Title"
    SUB_TITLE = "Modal Title"
    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Form(
                data_provider=self.data_provider,
                editing=self.editing,
                task_id=self.task_id,
            ),
            id="modal-content",
        )

    def action_close(self) -> None:
        self.app.pop_screen()
