from textual.app import ComposeResult
from textual.screen import ModalScreen
from xnoted.components.editPassword import EditPasswordForm
from xnoted.database.dataProvider import DataProvider


class EditPasswordModal(ModalScreen):
    """A modal dialog for editing."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "confirm", "Confirm"),
    ]
    BORDER_TITLE = "Edit password"

    def __init__(self, data_provider: DataProvider):
        super().__init__()
        self.data_provider = data_provider

    def compose(self) -> ComposeResult:
        yield EditPasswordForm(
            data_provider=self.data_provider,
            on_password_created=self.action_cancel,
        )

    def action_cancel(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()
