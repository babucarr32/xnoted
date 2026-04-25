from dataclasses import dataclass
from typing import Callable, cast

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input
from textual.app import Timer

from xnoted.database.dataProvider import DataProvider
from xnoted.utils.keyringService import DBKeyring

URL_ID = "url"
DATABASE_NAME_ID = "database"


@dataclass(frozen=True)
class FormData:
    url: str
    db_name: str


class InputContainer(Input):
    def __init__(self, border_title: str, id: str) -> None:
        super().__init__(id=id)
        self.border_title = border_title


class SyncConfigForm(Container):
    BINDINGS = [("ctrl+s", "submit", "Save form")]

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
        self._debounce_timer: Timer | None = None

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
            self._set_values(
                FormData(url=credentials.url, db_name=credentials.db_name or "")
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

    def _handle_submit(self) -> None:
        self.on_submit(self._build_form_data())

    def action_submit(self, debounce_ms: int = 150) -> None:
        if self._debounce_timer is not None:
            self._debounce_timer.stop()
        self._debounce_timer = self.set_timer(debounce_ms / 1000, self._handle_submit)
