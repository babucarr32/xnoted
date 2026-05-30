from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Static
from collections.abc import Callable
from xnoted.config.manager import ConfigHandler


class Confirm(Static):
    """A confirmation dialog widget."""

    BORDER_TITLE = "Press Enter to confirm or Esc to cancel"

    def __init__(self, title: str, message: str):
        super().__init__(id="confirm")
        self.modal_title = title
        self.modal_message = message

    def compose(self) -> ComposeResult:
        """Compose the modal content."""
        with Vertical(id="modal-dialog"):
            yield Label(self.modal_message, id="modal-message")


class ConfirmModal(ModalScreen):
    """A modal dialog for confirming actions."""

    def __init__(
        self,
        on_confirm: Callable[[], None],
        config_handler: ConfigHandler,
        title: str = "Confirm Action",
        message: str = "Are you sure you want to proceed?",
    ):
        """Initialize the confirmation modal.

        Args:
            on_confirm: Callback function to execute when confirmed
            title: The modal title
            message: The confirmation message to display
        """
        super().__init__()
        self.on_confirm = on_confirm
        self.modal_title = title
        self.config_handler = config_handler
        self.modal_message = message

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.save, action="confirm", description="Confirm", priority=True)
        self._bindings.bind(keys=kb.cancel, action="cancel", description="Cancel")

    def compose(self) -> ComposeResult:
        yield Confirm(self.modal_title, self.modal_message)

    def action_confirm(self) -> None:
        """Execute the confirmation callback and close modal."""
        self.app.pop_screen()
        self.on_confirm()

    def action_cancel(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()
