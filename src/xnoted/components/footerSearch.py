from textual.widgets import Static, Input
from xnoted.utils.constants import TASKS_ID
from xnoted.utils.database import Database
from typing import Iterator

class FooterSearch(Static):        
    BINDINGS = [
        ("escape", "escape", "Create new task"),
    ]

    def __init__(self, database: Database, toggle_search):
        super().__init__()
        self.database = database
        self.toggle_search = toggle_search
    
    def compose(self) -> Iterator[Input]:
        yield Input(
            placeholder="Search tasks...",
            id="search-input",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        tasks_widget = self.app.query_one(f"#{TASKS_ID}")
        tasks_widget.quick_search(event.value)

    def on_mount(self) -> None:
        self.query_one("#search-input").focus()

    def action_escape(self) -> None:
        self.toggle_search()
        task_widget = self.app.query_one("#tasks")
        task_widget.focus()
