import uuid
from textual.containers import Container
from textual.widgets import Input, TextArea, RadioSet, RadioButton, Label
from textual.app import ComposeResult
from xnoted.database.dataProvider import DataProvider, Project
from xnoted.components.tasks import Tasks
from typing import cast
from xnoted.utils.constants import (
    PROJECT_TITLE_ID,
    PROJECT_DESCRIPTION_ID,
    TASKS_ID,
    TASK_HEADER_ID,
    PROJECT_TASK_TYPE_ID,
    PROJECT_TYPE_ID,
    PROJECT_OTHER_TYPE_ID,
)
from typing import Iterator


class InputContainer(Input):
    BORDER_TITLE = "Project Title"

    def __init__(self) -> None:
        super().__init__(id=PROJECT_TITLE_ID)


class ContentContainer(TextArea):
    BORDER_TITLE = "Content"

    def __init__(self) -> None:
        super().__init__(
            id=PROJECT_DESCRIPTION_ID,
        )


class ProjectTypeContainer(RadioSet):
    BORDER_TITLE = "Type"

    def __init__(self) -> None:
        super().__init__(id=PROJECT_TYPE_ID)

    def compose(self) -> Iterator[RadioButton]:
        yield RadioButton("Task", id=PROJECT_TASK_TYPE_ID)
        yield RadioButton("Other", id=PROJECT_OTHER_TYPE_ID)


class CreateProjectForm(Container):
    def __init__(
        self,
        data_provider: DataProvider,
        title="",
        description="",
        project_id="",
        project_type=PROJECT_TASK_TYPE_ID,
        editing=False,
    ):
        super().__init__()
        self.data_provider = data_provider
        self.title = title
        self.description = description
        self.project_type = project_type
        self.editing = title
        self.project_id = project_id

    BINDINGS = [
        ("ctrl+s", "submit", "Save project form"),
    ]

    def _get_title_widget(self) -> InputContainer:
        return cast(InputContainer, self.query_one(f"#{PROJECT_TITLE_ID}"))

    def _get_task_type_widget(self, id=PROJECT_TASK_TYPE_ID) -> RadioButton:
        return cast(RadioButton, self.query_one(f"#{id}"))

    def _get_project_type_widget(self) -> RadioSet:
        return cast(RadioSet, self.query_one(f"#{PROJECT_TYPE_ID}"))

    def _get_description_widget(self) -> ContentContainer:
        return cast(ContentContainer, self.query_one(f"#{PROJECT_DESCRIPTION_ID}"))

    def on_mount(self) -> None:
        input_widget = self._get_title_widget()
        project_description_widget = self._get_description_widget()
        input_widget.value = self.title
        project_description_widget.text = self.description

        match self.project_type:
            case "task":
                radio_button_widget = self._get_task_type_widget()
                radio_button_widget.value = True
                return
            case _:
                radio_button_widget = self._get_task_type_widget(PROJECT_OTHER_TYPE_ID)
                radio_button_widget.value = True
                return

    def compose(self) -> ComposeResult:
        yield InputContainer()
        yield ContentContainer()
        yield ProjectTypeContainer()

    def handle_save_new(self) -> None:
        title = self._get_title_widget().value
        description = self._get_description_widget().text
        project_type = self._get_project_type_widget()

        if title:
            data = Project(
                id=str(uuid.uuid4()),
                title=title,
                description=description,
                type=cast(
                    str,
                    project_type.pressed_button.id
                    if project_type.pressed_button
                    else PROJECT_TASK_TYPE_ID,
                ),
            )
            self.data_provider.save_project(data)

    def handle_edit(self) -> None:
        updated_title = self._get_title_widget().value
        updated_description = self._get_description_widget().text
        project_type: RadioSet = self._get_project_type_widget()

        data = Project(
            id=self.project_id,
            title=updated_title,
            description=updated_description,
            type=cast(
                str,
                project_type.pressed_button.id
                if project_type.pressed_button
                else PROJECT_TASK_TYPE_ID,
            ),
        )

        self.data_provider.update_project(self.project_id, data)
        tasks_widget = cast(Tasks, self.app.query_one(f"#{TASKS_ID}"))

        task_header_label_widget = cast(Label, self.app.query_one(f"#{TASK_HEADER_ID}"))
        task_header_label_widget.update("self.data_provider.project_name")

        # Refresh only if task type is selected
        if (
            project_type.pressed_button
            and self.data_provider.project_type == project_type.pressed_button.id
        ):
            tasks_widget.refresh_tasks()
            task_header_label_widget = cast(
                Label, self.app.query_one(f"#{TASK_HEADER_ID}")
            )
            task_header_label_widget.update(self.data_provider.project_name)

    def action_submit(self) -> None:
        if self.editing:
            self.handle_edit()
        else:
            self.handle_save_new()
