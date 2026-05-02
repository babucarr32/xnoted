from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.createTaskForm import CreateTaskForm
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import CREATE_TASK_ID


class CreateTaskModal(ModalScreen):
    def __init__(
        self,
        data_provider: DataProvider,
        editing=False,
        task_id="",
    ):
        super().__init__(id=CREATE_TASK_ID)
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
            CreateTaskForm(
                data_provider=self.data_provider,
                editing=self.editing,
                task_id=self.task_id,
                on_submit=lambda: self.app.pop_screen(),
            ),
        )

    def action_close(self) -> None:
        self.app.pop_screen()
