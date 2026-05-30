from __future__ import annotations
from textual.widgets import Static, Input
from xnoted.utils.constants import TASKS_ID
from xnoted.database.dataProvider import DataProvider
from typing import Iterator, cast
from xnoted.config.manager import ConfigHandler


class FooterSearch(Static):
    def __init__(
        self, data_provider: DataProvider, toggle_search, config_handler: ConfigHandler
    ):
        super().__init__()
        self.data_provider = data_provider
        self.toggle_search = toggle_search
        self.config_handler = config_handler

    def compose(self) -> Iterator[Input]:
        yield Input(
            placeholder="Search tasks...",
            id="search-input",
        )

    def _get_tasks_widget(self):
        from xnoted.components.tasks import Tasks

        return cast(Tasks, self.app.query_one(f"#{TASKS_ID}"))

    def on_input_changed(self, event: Input.Changed) -> None:
        tasks_widget = self._get_tasks_widget()
        tasks_widget.quick_search(event.value)

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(
            keys=kb.save, action="submit", description="Submit search", priority=True
        )
        self.query_one("#search-input").focus()

    def action_submit(self) -> None:
        tasks_widget = self._get_tasks_widget()
        self.toggle_search()
        self.call_after_refresh(tasks_widget.focus_container_and_fist_child)
