import uuid
from textual.containers import Container
from textual.widgets import Input, TextArea
from textual.app import ComposeResult
from xnoted.utils.logger import get_logger
from xnoted.database.dataProvider import DataProvider, Task
from xnoted.components.tasks import Tasks
from textual.app import Timer
from typing import cast

logger = get_logger(__name__)

TITLE_ID = "title"
CONTENT_ID = "content"


class InputContainer(Input):
    BORDER_TITLE = "Title"

    def __init__(self) -> None:
        super().__init__(id=TITLE_ID)


class ContentContainer(TextArea):
    BORDER_TITLE = "Content"

    def __init__(self) -> None:
        super().__init__(
            language="markdown",
            id=CONTENT_ID,
            classes="editor",
        )


class Form(Container):
    def __init__(
        self,
        data_provider: DataProvider,
        title="",
        content="",
        editing=False,
        task_id="",
    ):
        super().__init__()
        self.title = title
        self.content = content
        self.editing = editing
        self.task_id = task_id
        self.data_provider = data_provider
        self._debounce_timer: None | Timer = None

    BINDINGS = [
        ("ctrl+s", "submit", "Save form"),
    ]

    def _get_title_widget(self) -> InputContainer:
        return cast(InputContainer, self.query_one(f"#{TITLE_ID}"))

    def _get_content_widget(self) -> ContentContainer:
        return cast(ContentContainer, self.query_one(f"#{CONTENT_ID}"))

    def on_mount(self) -> None:
        input_widget = cast(InputContainer, self.query_one(f"#{TITLE_ID}"))
        textarea_widget = cast(ContentContainer, self.query_one(f"#{CONTENT_ID}"))

        input_widget.value = self.title
        textarea_widget.text = self.content

    def compose(self) -> ComposeResult:
        yield InputContainer()
        yield ContentContainer()

    def handle_save_new(self) -> None:
        title = self._get_title_widget().value
        content = self._get_content_widget().text

        # Only title is required
        if title:
            data = Task(
                id=str(uuid.uuid4()),
                title=title,
                content=content,
                is_protected=0,
                project_id="",
                status=0,
            )
            if self.data_provider.is_storage_exist():
                self.data_provider.add_task(data)
            else:
                self.data_provider.save_task(data)

            tasks_widget = cast(Tasks, self.app.query_one("#tasks"))
            tasks_widget.refresh_tasks()

    def handle_edit(self) -> None:
        updated_title = self._get_title_widget().value
        updated_content = self._get_content_widget().text
        task = self.data_provider.get_task(self.task_id)

        if not task:
            logger.error(f"Task with id {self.task_id} not found")
            return None

        new_data = Task(
            id=task.id,
            title=updated_title,
            content=updated_content,
            is_protected=task.is_protected,
            project_id=task.project_id,
            status=task.status,
        )
        self.data_provider.update_task(self.task_id, new_data)

        tasks_widget = cast(Tasks, self.app.query_one("#tasks"))
        tasks_widget.refresh_tasks()

    def action_submit(self, debounce_ms: int = 150) -> None:
        # Cancel previous timer
        if self._debounce_timer is not None:
            self._debounce_timer.stop()

        if self.editing:
            self._debounce_timer = self.set_timer(
                debounce_ms / 1000, lambda: self.handle_edit()
            )

        else:
            self._debounce_timer = self.set_timer(
                debounce_ms / 1000, lambda: self.handle_save_new()
            )
