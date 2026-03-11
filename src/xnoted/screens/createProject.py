from typing import Iterator
from textual.containers import Vertical
from textual.screen import ModalScreen
from xnoted.components.createProjectForm import CreateProjectForm
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import (
    PROJECT_TASK_TYPE_ID,
    PROJECT_MODAL_CONTENT,
    CREATE_PROJECTS_ID,
)


class CreateProjectModal(ModalScreen):
    def __init__(
        self,
        data_provider: DataProvider,
        title="",
        description="",
        project_id="",
        project_type=PROJECT_TASK_TYPE_ID,
        editing=False,
    ):
        super().__init__(id=CREATE_PROJECTS_ID)
        self.data_provider = data_provider
        self.title = title
        self.project_id = project_id
        self.description = description
        self.project_type = project_type
        self.editing = title

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> Iterator[Vertical]:
        yield Vertical(
            CreateProjectForm(
                data_provider=self.data_provider,
                title=self.title,
                project_id=self.project_id,
                description=self.description,
                editing=self.editing,
                project_type=self.project_type,
            ),
            id=PROJECT_MODAL_CONTENT,
        )

    def action_close(self) -> None:
        self.app.pop_screen()
