from enum import Enum
import json
import pyperclip
from textual.screen import ModalScreen
from collections.abc import Callable
from textual.widgets import Label, ListView, ListItem
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import COPY_TASK, EXPORT_ERROR_TITLE
from typing import cast
from textual.app import ComposeResult
from xnoted.utils.logger import get_logger
from xnoted.config.manager import ConfigHandler


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
        self,
        data_provider: DataProvider,
        close_app: Callable[[], None],
        item_id: str,
        config_handler: ConfigHandler,
    ):
        super().__init__(id=COPY_TASK)
        self.has_task_result = True
        self.data_provider = data_provider
        self.close_app = close_app
        self.item_id = item_id
        self.config_handler = config_handler

    BORDER_TITLE = "Copy"

    OPTIONS: list[dict[str, str]] = [
        {"id": cast(str, OptionIDS.COPY_TITLE), "title": "Copy title"},
        {"id": cast(str, OptionIDS.COPY_CONTENT), "title": "Copy content"},
        {"id": cast(str, OptionIDS.COPY_ALL), "title": "Copy all"},
    ]

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.copy_task

        self._bindings.bind(
            keys=kb.cursor_up, action="cursor_up", description="Cursor up"
        )
        self._bindings.bind(
            keys=kb.cursor_down, action="cursor_down", description="Cursor down"
        )

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
            self.notify(
                f"Task not found for id {opt_id}",
                title=EXPORT_ERROR_TITLE,
                severity="error",
            )
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
    def __init__(
        self, data_provider: DataProvider, item_id: str, config_handler: ConfigHandler
    ):
        self.data_provider = data_provider
        self.item_id = item_id
        self.config_handler = config_handler
        super().__init__()

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.cancel, action="close", description="Close modal")

    def compose(self) -> ComposeResult:
        yield CopyTask(
            data_provider=self.data_provider,
            close_app=self.action_close,
            item_id=self.item_id,
            config_handler=self.config_handler,
        )

    def action_close(self) -> None:
        self.app.pop_screen()
