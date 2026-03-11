from typing import Callable
from textual.containers import Container
from typing import cast
from textual.app import Timer
from textual.widgets import Input, Static
from textual.app import ComposeResult
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import (
    PASSWORD_ID,
    RE_PASSWORD_ID,
    CREATE_PASSWORD_ID,
    CREATE_PASSWORD_FORM_CONTAINER_ID,
)


class InputContainer(Input):
    def __init__(self, id: str, border_title: str) -> None:
        super().__init__(id=id)
        self.border_title = border_title


class FormContainer(Static):
    """A confirmation dialog widget."""

    def __init__(self):
        super().__init__(id=CREATE_PASSWORD_FORM_CONTAINER_ID)

    def compose(self) -> ComposeResult:
        """Compose the modal content."""
        yield InputContainer(id=PASSWORD_ID, border_title="Password")
        yield InputContainer(id=RE_PASSWORD_ID, border_title="Re-Password")


class Form(Container):
    def __init__(
        self, data_provider: DataProvider, on_password_created: Callable[[], None]
    ):
        super().__init__(id=CREATE_PASSWORD_ID)
        self.data_provider = data_provider
        self._debounce_timer: Timer | None = None
        self.on_password_created = on_password_created

    BINDINGS = [
        ("ctrl+s", "submit", "Save form"),
    ]

    @property
    def is_password_created(self):
        return self.is_password_set

    def compose(self) -> ComposeResult:
        yield FormContainer()

    def handle_create_password(self) -> None:
        password = cast(InputContainer, self.query_one(f"#{PASSWORD_ID}")).value
        re_password = cast(InputContainer, self.query_one(f"#{RE_PASSWORD_ID}")).value

        if password != re_password:
            password_widget = self.query_one(f"#{PASSWORD_ID}")
            password_widget.border_title = (
                f"{password_widget.border_title} / Unmatched password"
            )
            return
        self.data_provider.save_password(password)
        self.on_password_created()

    def action_submit(self, debounce_ms: int = 150) -> None:
        # Cancel previous timer
        if self._debounce_timer is not None:
            self._debounce_timer.stop()

        self._debounce_timer = self.set_timer(
            debounce_ms / 1000, lambda: self.handle_create_password()
        )
