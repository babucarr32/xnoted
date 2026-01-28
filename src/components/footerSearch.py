from textual.widgets import Static, Input
from textual.reactive import reactive
from src.utils.database import Database

class FooterSearch(Static):    
    is_searching = reactive(False)
    
    BINDINGS = [
        ("escape", "escape", "Create new task"),
    ]

    def __init__(self, database: Database, toggle_search):
        super().__init__()
        self.database = database
        self.toggle_search = toggle_search
    
    def compose(self):
        yield Input(
            placeholder="Search tasks...",
            id="search-input",
        )

    def on_mount(self):
        self.query_one("#search-input").focus()

    def action_escape(self):
        self.toggle_search()
        task_widget = self.app.query_one("#tasks")
        task_widget.focus()
