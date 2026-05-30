from textual.app import ComposeResult
from textual.screen import ModalScreen
from xnoted.components.editPassword import EditPasswordForm
from xnoted.config.manager import ConfigHandler
from xnoted.database.dataProvider import DataProvider


class EditPasswordModal(ModalScreen):
    """A modal dialog for editing."""

    BORDER_TITLE = "Edit password"

    def __init__(self, data_provider: DataProvider, config_handler: ConfigHandler):
        super().__init__()
        self.data_provider = data_provider
        self.config_handler = config_handler

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.save, action="confirm", description="Confirm")
        self._bindings.bind(keys=kb.cancel, action="cancel", description="Cancel")

    def compose(self) -> ComposeResult:
        yield EditPasswordForm(
            data_provider=self.data_provider,
            on_password_created=self.action_cancel,
            config_handler=self.config_handler,
        )

    def action_cancel(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()
