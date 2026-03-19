from __future__ import annotations
from textual.widgets import Static, Input
from xnoted.utils.constants import TASKS_ID
from xnoted.database.dataProvider import DataProvider
from typing import Iterator, cast


class FooterSearch(Static):
    BINDINGS = [
        ("escape", "escape", "Create new task"),
    ]

    def __init__(self, data_provider: DataProvider, toggle_search):
        super().__init__()
        self.data_provider = data_provider
        self.toggle_search = toggle_search

    def compose(self) -> Iterator[Input]:
        yield Input(
            placeholder="Search tasks...",
            id="search-input",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        from xnoted.components.tasks import Tasks
        tasks_widget = cast(Tasks, self.app.query_one(f"#{TASKS_ID}"))
        tasks_widget.quick_search(event.value)

    def on_mount(self) -> None:
        self.query_one("#search-input").focus()

    def action_escape(self) -> None:
        self.toggle_search()
        task_widget = self.app.query_one(f"#{TASKS_ID}")
        task_widget.focus()
