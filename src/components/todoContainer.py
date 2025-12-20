from textual.widgets import Input
from src.components.todos import Todos
from textual.app import ComposeResult
from textual.containers import Container

SEARCH_ID = "search"

class TodoContainer(Container):
    BORDER_TITLE = "Search Todos"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id=SEARCH_ID)
        yield Todos()
    
    def on_mount(self):
        """Focus the search input when container is mounted"""
        self.query_one(f"#{SEARCH_ID}").focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.log(event.value)
        todos_widget = self.app.query_one(Todos)
        todos_widget.quick_search(event.value)
