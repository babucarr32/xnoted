from textual.app import ComposeResult, Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Static
from collections.abc import Callable


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

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm", priority=True),
    ]

    def __init__(
        self,
        on_confirm: Callable[[], None],
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
        self.modal_message = message

    def compose(self) -> ComposeResult:
        yield Confirm(self.modal_title, self.modal_message)

    def action_confirm(self) -> None:
        """Execute the confirmation callback and close modal."""
        self.app.pop_screen()
        self.on_confirm()

    def action_cancel(self) -> None:
        """Close the modal without confirming."""
        self.app.pop_screen()
