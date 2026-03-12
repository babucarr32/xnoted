from enum import Enum
import json
import pyperclip
from textual.screen import ModalScreen
from collections.abc import Callable
from textual.widgets import Label, ListView, ListItem
from xnoted.database.dataProvider import DataProvider
from textual.binding import Binding
from xnoted.utils.constants import COPY_TASK
from typing import cast
from textual.app import ComposeResult
from xnoted.utils.logger import get_logger

logger = get_logger(__name__)


class OptionIDS(Enum):
    COPY_ALL = "copy-all"
    COPY_TITLE = "copy-title"
    COPY_CONTENT = "copy-content"


class CopyItem(ListItem):
    def __init__(self, *args, item_id: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_id = item_id


class CopyTask(ListView):
    def __init__(
        self, data_provider: DataProvider, close_app: Callable[[], None], item_id: str
    ):
        super().__init__(id=COPY_TASK)
        self.has_task_result = True
        self.data_provider = data_provider
        self.close_app = close_app
        self.item_id = item_id

    BORDER_TITLE = "Copy"
    BINDINGS = [
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
    ]

    OPTIONS: list[dict[str, str]] = [
        {"id": cast(str, OptionIDS.COPY_TITLE), "title": "Copy title"},
        {"id": cast(str, OptionIDS.COPY_CONTENT), "title": "Copy content"},
        {"id": cast(str, OptionIDS.COPY_ALL), "title": "Copy all"},
    ]

    def on_mount(self) -> None:
        self.load_options()

    def load_options(self) -> None:
        self.clear()

        for opt in self.OPTIONS:
            title = opt.get("title")
            opt_id = opt.get("id")

            if opt_id and title:
                list_item = CopyItem(Label(f"{title}"), item_id=opt_id)
                self.append(list_item)

    def on_list_view_selected(self, event: ListView.Highlighted) -> None:
        opt_id = cast(CopyItem, event.item).item_id
        try:
            selected_item_id = OptionIDS(opt_id)
        except ValueError:
            return

        item_data = self.data_provider.get_task(self.item_id)
        if not item_data:
            logger.error(f"Task not found for id {opt_id}")
            return None

        match selected_item_id:
            case OptionIDS.COPY_ALL:
                pyperclip.copy(json.dumps(item_data.to_dict(), indent=2))
            case OptionIDS.COPY_CONTENT:
                pyperclip.copy(item_data.content)
            case OptionIDS.COPY_TITLE:
                pyperclip.copy(item_data.title)

        self.close_app()


class CopyTaskModal(ModalScreen):
    def __init__(self, data_provider: DataProvider, item_id: str):
        self.data_provider = data_provider
        self.item_id = item_id
        super().__init__()

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> ComposeResult:
        yield CopyTask(
            data_provider=self.data_provider,
            close_app=self.action_close,
            item_id=self.item_id,
        )

    def action_close(self) -> None:
        self.app.pop_screen()
