import uuid
from textual.containers import Container
from textual.widgets import Input, TextArea
from textual.app import ComposeResult
from src.utils.storage import Storage
from src.components.todos import Todos
from src.utils.constants import DB_PATH

TITLE_ID = "title"
CONTENT_ID = "content"

class Form(Container):
    BINDINGS = [
        ("ctrl+s", "submit", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter title here...", id=TITLE_ID)
        yield TextArea(
            placeholder="Enter content here....",
            language="markdown",
            id=CONTENT_ID,
            classes="editor",
        )

    def action_submit(self) -> None:
        storage = Storage(DB_PATH)
        title = self.query_one(f"#{TITLE_ID}").value
        content = self.query_one(f"#{CONTENT_ID}").text

        # Only title is required
        if title:
            data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "content": content,
            }

            if storage.is_storage_exist():
                storage.append(data)
            else:
                storage.save(data)

            self.log(f"Title: {title}")
            self.log(f"Content: {content}")

            todos_widget = self.app.query_one(Todos)
            todos_widget.refresh_todos()
