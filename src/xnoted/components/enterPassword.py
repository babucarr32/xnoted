from textual.containers import Container
from typing import cast
from textual.app import Timer
from collections.abc import Callable
from textual.widgets import Input, Static
from textual.app import ComposeResult
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import (
    PASSWORD_ID,
    ENTER_PASSWORD_ID,
    ENTER_PASSWORD_FORM_CONTAINER_ID,
)


class InputContainer(Input):
    def __init__(self, id: str, border_title: str) -> None:
        super().__init__(id=id, password=True)
        self.border_title = border_title


class FormContainer(Static):
    """A confirmation dialog widget."""

    def __init__(self):
        super().__init__(
            id=ENTER_PASSWORD_FORM_CONTAINER_ID,
        )

    def compose(self) -> ComposeResult:
        """Compose the modal content."""
        yield InputContainer(id=PASSWORD_ID, border_title="Password")


class EnterPasswordForm(Container):
    def __init__(
        self,
        data_provider: DataProvider,
        close_app: Callable[[], None],
        on_password_valid: Callable[[], None],
    ):
        super().__init__(id=ENTER_PASSWORD_ID)
        self.data_provider = data_provider
        self.close_app = close_app
        self.on_password_valid = on_password_valid
        self._debounce_timer: Timer | None = None

    BINDINGS = [
        ("ctrl+s", "submit", "Validate password"),
    ]

    @property
    def is_password_created(self):
        return self.is_password_set

    def compose(self) -> ComposeResult:
        yield FormContainer()

    def handle_validate_password(self) -> None:
        password = cast(InputContainer, self.query_one(f"#{PASSWORD_ID}")).value
        is_valid_password = self.data_provider.verify_password(password)

        if not is_valid_password:
            password_widget = self.query_one(f"#{PASSWORD_ID}")
            password_widget.border_title = (
                f"{password_widget.border_title} / Invalid password"
            )
        else:
            self.on_password_valid()
            self.close_app()

    def action_submit(self, debounce_ms: int = 150) -> None:
        # Cancel previous timer
        if self._debounce_timer is not None:
            self._debounce_timer.stop()

        self._debounce_timer = self.set_timer(
            debounce_ms / 1000, lambda: self.handle_validate_password()
        )
