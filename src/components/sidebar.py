import uuid
from textual.containers import Container
from textual.widgets import Input, TextArea
from textual.app import ComposeResult
from src.utils.database import Database

TITLE_ID = "title"
CONTENT_ID = "content"


class InputContainer(Input):
    BORDER_TITLE = "Title"

    def __init__(self):
        super().__init__(id=TITLE_ID)


class ContentContainer(TextArea):
    BORDER_TITLE = "Content"

    def __init__(self):
        super().__init__(
            language="markdown",
            id=CONTENT_ID,
            classes="editor",
        )


class Form(Container):
    def __init__(
        self,
        database: Database,
        title="",
        content="",
        editing=False,
        todo_id="",
    ):
        super().__init__()
        self.title = title
        self.content = content
        self.editing = editing
        self.todo_id = todo_id
        self.database = database

    BINDINGS = [
        ("ctrl+s", "submit", "Save form"),
    ]

    def on_mount(self):
        input_widget = self.query_one(f"#{TITLE_ID}")
        textarea_widget = self.query_one(f"#{CONTENT_ID}")

        input_widget.value = self.title
        textarea_widget.text = self.content

    def compose(self) -> ComposeResult:
        yield InputContainer()
        yield ContentContainer()

    def handle_save_new(self) -> None:
        title = self.query_one(f"#{TITLE_ID}").value
        content = self.query_one(f"#{CONTENT_ID}").text

        # Only title is required
        if title:
            data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "content": content,
            }
            if self.database.is_storage_exist():
                self.database.append(data)
            else:
                self.database.save(data)

            todos_widget = self.app.query_one("#todos")
            todos_widget.refresh_todos()

    def handle_edit(self) -> None:
        updated_title = self.query_one(f"#{TITLE_ID}").value
        updated_content = self.query_one(f"#{CONTENT_ID}").text

        new_data = {
            "title": updated_title,
            "content": updated_content,
        }

        self.database.update_task(self.todo_id, new_data)

        todos_widget = self.app.query_one("#todos")
        todos_widget.refresh_todos()

    def action_submit(self) -> None:
        if self.editing:
            self.handle_edit()
        else:
            self.handle_save_new()
