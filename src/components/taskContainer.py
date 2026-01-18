from textual.widgets import Input
from src.components.tasks import Tasks
from textual.app import ComposeResult
from textual.containers import Container
from src.utils.database import Database
from src.utils.constants import TASK_CONTAINER_ID

SEARCH_ID = "search"

class TaskContainer(Container):
    def __init__(self, database: Database):
        super().__init__(id=TASK_CONTAINER_ID)
        self.database = database
        self.border_title = f"Project {self.database.project_name}"

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id=SEARCH_ID)
        yield Tasks(database=self.database)
    
    def on_mount(self):
        """Focus the search input when container is mounted"""
        self.query_one(f"#{SEARCH_ID}").focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.log(event.value)
        tasks_widget = self.app.query_one(Tasks)
        tasks_widget.quick_search(event.value)
