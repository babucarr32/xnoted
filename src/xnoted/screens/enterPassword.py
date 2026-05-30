from textual.app import ComposeResult
from textual.screen import ModalScreen
from xnoted.components.enterPassword import EnterPasswordForm
from typing import Callable, Any
from xnoted.database.dataProvider import DataProvider
from xnoted.config.manager import ConfigHandler


class EnterPasswordModal(ModalScreen):
    """A modal dialog for confirming actions."""

    BORDER_TITLE = "Create password"

    def __init__(
        self,
        data_provider: DataProvider,
        config_handler: ConfigHandler,
        on_password_valid: Callable[[], Any],
    ):
        super().__init__()
        self.data_provider = data_provider
        self.on_password_valid = on_password_valid
        self.config_handler = config_handler

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.cancel, action="cancel", description="Cancel")

    def compose(self) -> ComposeResult:
        yield EnterPasswordForm(
            data_provider=self.data_provider,
            close_app=self.action_cancel,
            on_password_valid=self.on_password_valid,
            config_handler=self.config_handler,
        )

    def action_cancel(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()
