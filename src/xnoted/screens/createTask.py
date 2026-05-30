from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.createTaskForm import CreateTaskForm
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import CREATE_TASK_ID
from xnoted.config.manager import ConfigHandler


class CreateTaskModal(ModalScreen):
    def __init__(
        self,
        config_handler: ConfigHandler,
        data_provider: DataProvider,
        editing=False,
        task_id="",
    ):
        super().__init__(id=CREATE_TASK_ID)
        self.editing = editing
        self.config_handler = config_handler
        self.task_id = task_id
        self.data_provider = data_provider

    TITLE = "Modal Title"
    SUB_TITLE = "Modal Title"

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.cancel, action="close", description="Close modal")

    def compose(self) -> ComposeResult:
        yield Vertical(
            CreateTaskForm(
                data_provider=self.data_provider,
                editing=self.editing,
                task_id=self.task_id,
                on_submit=lambda: self.action_close(),
                config_handler=self.config_handler,
            ),
        )

    def action_close(self) -> None:
        self.app.pop_screen()
