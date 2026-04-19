from typing import Callable
from textual import work
import asyncio
from xnoted.components.spinner import Spinner
from textual.containers import Container
from typing import cast
from textual.app import Timer
from textual.widgets import Input, Static
from textual.app import ComposeResult
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import (
    PASSWORD_ID,
    OLD_PASSWORD_ID,
    RE_PASSWORD_ID,
    CREATE_PASSWORD_ID,
    CREATE_PASSWORD_FORM_CONTAINER_ID,
)


OLD_PASSWORD_BORDER_TITLE = "Old Password"
PASSWORD_BORDER_TITLE = "Password"
RE_PASSWORD_BORDER_TITLE = "Re-Password"


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
        yield InputContainer(id=OLD_PASSWORD_ID, border_title=OLD_PASSWORD_BORDER_TITLE)
        yield InputContainer(id=PASSWORD_ID, border_title=PASSWORD_BORDER_TITLE)
        yield InputContainer(id=RE_PASSWORD_ID, border_title=RE_PASSWORD_BORDER_TITLE)


class EditPasswordForm(Container):
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

    def compose(self) -> ComposeResult:
        yield FormContainer()

    import asyncio

    async def handle_edit_password(self) -> bool:
        old_password = cast(InputContainer, self.query_one(f"#{OLD_PASSWORD_ID}")).value
        password = cast(InputContainer, self.query_one(f"#{PASSWORD_ID}")).value
        re_password = cast(InputContainer, self.query_one(f"#{RE_PASSWORD_ID}")).value

        is_old_password_valid = self.data_provider.verify_password(old_password)

        old_password_widget = self.query_one(f"#{OLD_PASSWORD_ID}")
        password_widget = self.query_one(f"#{PASSWORD_ID}")

        def reset_border_title():
            old_password_widget.border_title = OLD_PASSWORD_BORDER_TITLE
            password_widget.border_title = PASSWORD_BORDER_TITLE

        if not is_old_password_valid:
            reset_border_title()
            old_password_widget.border_title = (
                f"{old_password_widget.border_title} / Invalid password"
            )
            return False

        if password != re_password:
            reset_border_title()
            password_widget.border_title = (
                f"{password_widget.border_title} / Unmatched password"
            )
            return False

        await asyncio.sleep(0)  # let spinner render
        self.data_provider.edit_password(password)
        self.on_password_created()

        return True

    @work(exclusive=True)
    async def action_submit(self, debounce_ms: int = 150) -> None:
        spinner = cast(Spinner, self.app.query_one(Spinner))
        await spinner.wrap(self.handle_edit_password(), "Re encrypting...")
