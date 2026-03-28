from textual.app import ComposeResult
from textual.widgets import Static, Label
from xnoted.utils.constants import FOOTER_LABEL_ID
from xnoted.components.spinner import Spinner


class FooterLabel(Static):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(
            "Move down: j | Move up: k | Edit task: e | Copy task: c | Delete task: d | "
            "Previous status: ← | Next status: → | Body down: Ctrl+d | "
            "Body up: Ctrl+u | Search: /",
            id=FOOTER_LABEL_ID,
        )
        yield Spinner()
