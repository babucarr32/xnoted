from textual.containers import Vertical
from textual.screen import ModalScreen
from src.components.sidebar import Form


class CreateToDoModal(ModalScreen):
    TITLE = "Modal Title"
    SUB_TITLE = "Modal Title"
    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self):
        yield Vertical(Form(), id="modal-content")

    def action_close(self): 
        self.app.pop_screen()
