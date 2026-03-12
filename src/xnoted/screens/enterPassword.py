from textual.app import ComposeResult
from textual.screen import ModalScreen
from xnoted.components.enterPassword import EnterPasswordForm
from typing import Callable
from xnoted.database.dataProvider import DataProvider


class EnterPasswordModal(ModalScreen):
    """A modal dialog for confirming actions."""

    BINDINGS = [("escape", "cancel", "Cancel")]
    BORDER_TITLE = "Create password"

    def __init__(
        self,
        data_provider: DataProvider,
        on_password_valid: Callable[[], None],
    ):
        super().__init__()
        self.data_provider = data_provider
        self.on_password_valid = on_password_valid

    def compose(self) -> ComposeResult:
        yield EnterPasswordForm(
            data_provider=self.data_provider,
            close_app=self.action_cancel,
            on_password_valid=self.on_password_valid,
        )

    def action_cancel(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()
