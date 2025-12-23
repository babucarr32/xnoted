from textual.containers import Vertical
from textual.screen import ModalScreen
from src.components.sidebar import Form
from src.utils.database import Database


class CreateToDoModal(ModalScreen):
    def __init__(
        self, database: Database, title="", content="", editing=False, todo_id=""
    ):
        super().__init__(id="createToDoModal")
        self.title = title
        self.content = content
        self.editing = editing
        self.todo_id = todo_id
        self.database = database

    TITLE = "Modal Title"
    SUB_TITLE = "Modal Title"
    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self):
        yield Vertical(
            Form(
                database=self.database,
                title=self.title,
                content=self.content,
                editing=self.editing,
                todo_id=self.todo_id,
            ),
            id="modal-content",
        )

    def action_close(self):
        self.app.pop_screen()
