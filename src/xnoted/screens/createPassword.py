from typing import Callable
from textual.app import ComposeResult
from textual.screen import ModalScreen
from xnoted.components.createPassword import CreatePasswordForm
from xnoted.database.dataProvider import DataProvider
from xnoted.config.manager import ConfigHandler


class CreatePasswordModal(ModalScreen):
    """A modal dialog for creating password"""

    BORDER_TITLE = "Create password"

    def __init__(
        self,
        data_provider: DataProvider,
        on_password_created: Callable[[], None],
        config_handler: ConfigHandler,
    ):
        super().__init__()
        self.data_provider = data_provider
        self.on_password_created = on_password_created
        self.config_handler = config_handler

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.save, action="confirm", description="Confirm")
        self._bindings.bind(keys=kb.cancel, action="cancel", description="Cancel")

    def compose(self) -> ComposeResult:
        yield CreatePasswordForm(
            data_provider=self.data_provider,
            on_password_created=self.on_password_created,
            config_handler=self.config_handler
        )

    def action_cancel(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()
