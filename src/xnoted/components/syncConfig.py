from dataclasses import dataclass
from xnoted.errors.errorHandler import ErrorHandler
from typing import Callable, cast

from xnoted.utils.helpers import mask
from xnoted.screens.confirm import ConfirmModal
from xnoted.screens.enterPassword import EnterPasswordModal
from textual.app import ComposeResult, Binding
from textual.containers import Container
from textual.widgets import Input
from textual.app import Timer
from xnoted.utils.constants import ERROR_TITLE
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.keyringService import DBKeyring
from xnoted.utils.logger import get_logger

URL_ID = "url"
DATABASE_NAME_ID = "database"

logger = get_logger(__name__)


@dataclass(frozen=True)
class FormData:
    url: str
    db_name: str


class InputContainer(Input):
    def __init__(self, border_title: str, id: str) -> None:
        super().__init__(id=id)
        self.border_title = border_title


class SyncConfigForm(Container):
    BINDINGS = [Binding("enter", "submit", "Save form", priority=True)]

    def __init__(
        self,
        on_submit: Callable[[FormData], None],
        data_provider: DataProvider,
        task_id: str = "",
    ) -> None:
        super().__init__()
        self.task_id = task_id
        self.data_provider = data_provider
        self.on_submit = on_submit
        self._actual_url = ""
        self._debounce_timer: Timer | None = None

    @property
    def is_form_dirty(self) -> bool:
        db_keyring = DBKeyring()
        credentials = db_keyring.get_credentials()

        if not credentials:
            self._notify()
            return False

        url = self._get_url_widget().value
        db_name = self._get_db_name_widget().value

        return self._mask(credentials.url) != url or db_name != credentials.db_name

    @property
    def _is_url_invalid(self):
        url = self._get_url_widget().value
        db_keyring = DBKeyring()
        credentials = db_keyring.get_credentials()

        return True if "*" in url and self._mask(credentials.url) != url else False

    @property
    def _is_url_unchanged(self):
        url = self._get_url_widget().value
        db_keyring = DBKeyring()
        credentials = db_keyring.get_credentials()

        return self._mask(credentials.url) == url

    def _mask(self, data: str):
        return mask(data, 40)

    def _get_url_widget(self) -> InputContainer:
        return cast(InputContainer, self.query_one(f"#{URL_ID}"))

    def _get_db_name_widget(self) -> InputContainer:
        return cast(InputContainer, self.query_one(f"#{DATABASE_NAME_ID}"))

    def _set_values(self, data: FormData) -> None:
        self._get_url_widget().value = data.url
        self._get_db_name_widget().value = data.db_name

    def on_mount(self) -> None:
        db_keyring = DBKeyring()
        credentials = db_keyring.get_credentials()

        if credentials:
            self._actual_url = credentials.url
            self._set_values(
                FormData(url=self._mask(credentials.url), db_name=credentials.db_name)
            )
        else:
            self._set_values(FormData(url="", db_name=""))

    def compose(self) -> ComposeResult:
        yield InputContainer(border_title="Database url", id=URL_ID)
        yield InputContainer(border_title="Database name", id=DATABASE_NAME_ID)

    def _build_form_data(self) -> FormData:
        return FormData(
            url=self._get_url_widget().value,
            db_name=self._get_db_name_widget().value,
        )

    def _notify(self):
        self.notify(
            "One or more missing credentials",
            title=ERROR_TITLE,
            severity="error",
        )
        logger.error("One or more missing credentials not found")

    def _handle_submit(self) -> None:
        form_data = self._build_form_data()

        if self._is_url_unchanged:
            # Use the original unmasked url
            form_data = FormData(url=self._actual_url, db_name=form_data.db_name)
        self.app.push_screen(
            EnterPasswordModal(
                data_provider=self.data_provider,
                on_password_valid=lambda: self.on_submit(form_data),
            )
        )

    def action_submit(self, debounce_ms: int = 150) -> None:
        if self._is_url_invalid:
            self.app.push_screen(
                ConfirmModal(
                    on_confirm=self._handle_submit,
                    title="Alert",
                    message="Invalid URL detected, are you sure you want to continue?",
                )
            )
            return
        self._handle_submit()
