from enum import Enum
import json
import pyperclip
from textual.screen import ModalScreen
from collections.abc import Callable
from textual.widgets import Label, ListView, ListItem
from xnoted.utils.database import Database
from textual.binding import Binding
from xnoted.utils.constants import COPY_TASK


class OptionIDS(Enum):
    COPY_ALL = "copy-all"
    COPY_TITLE = "copy-title"
    COPY_CONTENT = "copy-content"


class CopyTask(ListView):
    def __init__(self, database: Database, close_app: Callable[[], None], item_id: str):
        super().__init__(id=COPY_TASK)
        self.has_task_result = True
        self.database = database
        self.close_app = close_app
        self.item_id = item_id

    BORDER_TITLE = "Copy"
    BINDINGS = [
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
    ]

    OPTIONS: list[dict[str, str]] = [
        {"id": OptionIDS.COPY_TITLE, "title": "Copy title"},
        {"id": OptionIDS.COPY_CONTENT, "title": "Copy content"},
        {"id": OptionIDS.COPY_ALL, "title": "Copy all"},
    ]

    def on_mount(self) -> None:
        self.load_options()

    def load_options(self) -> None:
        self.clear()

        for opt in self.OPTIONS:
            title = opt.get("title")
            opt_id = opt.get("id")
            list_item = ListItem(Label(f"{title}"))
            list_item.item_id = opt_id
            self.append(list_item)

    def on_list_view_selected(self, event: ListView.Highlighted) -> None:
        opt_id = event.item.item_id
        try:
            selected_item_id = OptionIDS(opt_id)
        except ValueError:
            return

        item_data = self.database.get_task(self.item_id)
        if not item_data:
            raise RuntimeError(f"Task not found for id {opt_id}")

        match selected_item_id:
            case OptionIDS.COPY_ALL:
                pyperclip.copy(json.dumps(item_data, indent=2))
            case OptionIDS.COPY_CONTENT:
                pyperclip.copy(item_data.get("content"))
            case OptionIDS.COPY_TITLE:
                pyperclip.copy(item_data.get("title"))

        self.close_app()


class CopyTaskModal(ModalScreen):
    def __init__(self, database: Database, item_id: str):
        self.database = database
        self.item_id = item_id
        super().__init__()

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> None:
        yield CopyTask(
            database=self.database, close_app=self.action_close, item_id=self.item_id
        )

    def action_close(self) -> None:
        self.app.pop_screen()
