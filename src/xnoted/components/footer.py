from textual.widgets import Static
from xnoted.database.dataProvider import DataProvider
from textual.reactive import reactive
from xnoted.components.footerLabel import FooterLabel
from xnoted.components.footerSearch import FooterSearch
from xnoted.utils.constants import FOOTER_ID, TASKS_ID
from typing import Iterator, cast
from xnoted.config.manager import ConfigHandler


class Footer(Static):
    is_searching = reactive(False, recompose=True)

    def __init__(self, data_provider: DataProvider, config_handler: ConfigHandler):
        super().__init__(id=FOOTER_ID)
        self.data_provider = data_provider
        self.config_handler = config_handler

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.cancel, action="cancel", description="Cancel")

    def compose(self) -> Iterator[FooterLabel | FooterSearch]:
        if not self.is_searching:
            yield FooterLabel()
        else:
            yield FooterSearch(
                data_provider=self.data_provider,
                toggle_search=self.toggle_search,
                config_handler=self.config_handler,
            )

    def toggle_search(self) -> None:
        """Toggle between help text and search input"""
        self.is_searching = not self.is_searching

    def action_cancel(self):
        from xnoted.components.tasks import Tasks

        tasks_widget = cast(Tasks, self.app.query_one(f"#{TASKS_ID}"))
        self.is_searching = False
        tasks_widget.load_tasks()
        tasks_widget.focus_container_and_fist_child()
