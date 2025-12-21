from textual.containers import Vertical
from textual.screen import ModalScreen
from src.components.sidebar import Form


class CreateToDoModal(ModalScreen):
    def __init__(self, title="", content="", editing=False, todo_id=""):
        super().__init__(id="createToDoModal")
        self.title = title
        self.content = content
        self.editing = editing
        self.todo_id = todo_id

    TITLE = "Modal Title"
    SUB_TITLE = "Modal Title"
    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self):
        yield Vertical(
            Form(self.title, self.content, self.editing, self.todo_id),
            id="modal-content",
        )

    def action_close(self):
        self.app.pop_screen()
