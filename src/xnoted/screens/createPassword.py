from typing import Callable
from textual.app import ComposeResult
from textual.screen import ModalScreen
from xnoted.components.createPassword import CreatePasswordForm
from xnoted.database.dataProvider import DataProvider


class CreatePasswordModal(ModalScreen):
    """A modal dialog for creating password"""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "confirm", "Confirm"),
    ]
    BORDER_TITLE = "Create password"

    def __init__(
        self, data_provider: DataProvider, on_password_created: Callable[[], None]
    ):
        super().__init__()
        self.data_provider = data_provider
        self.on_password_created = on_password_created

    def compose(self) -> ComposeResult:
        yield CreatePasswordForm(
            data_provider=self.data_provider,
            on_password_created=self.on_password_created,
        )

    def action_cancel(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()
