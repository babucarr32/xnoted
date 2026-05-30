from typing import Iterator, Callable, Any
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.createProjectForm import CreateProjectForm
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import (
    PROJECT_TASK_TYPE_ID,
    PROJECT_MODAL_CONTENT,
    CREATE_PROJECTS_ID,
)
from xnoted.config.manager import ConfigHandler



class CreateProjectModal(ModalScreen):
    def __init__(
        self,
        data_provider: DataProvider,
        config_handler: ConfigHandler,
        project_id="",
        project_type=PROJECT_TASK_TYPE_ID,
        on_submit=Callable[[], Any],
        editing=False,
    ):
        super().__init__(id=CREATE_PROJECTS_ID)
        self.data_provider = data_provider
        self.project_id = project_id
        self.project_type = project_type
        self.editing = editing
        self.config_handler = config_handler
        self.on_submit = on_submit

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.cancel, action="close", description="Close modal")

    def compose(self) -> Iterator[Vertical]:
        yield Vertical(
            CreateProjectForm(
                data_provider=self.data_provider,
                project_id=self.project_id,
                config_handler=self.config_handler,
                editing=self.editing,
                project_type=self.project_type,
                on_submit=lambda: (self.app.pop_screen(), self.on_submit()),
            ),
            id=PROJECT_MODAL_CONTENT,
        )

    def action_close(self) -> None:
        self.app.pop_screen()
