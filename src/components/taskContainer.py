from src.components.tasks import Tasks
from textual.app import ComposeResult
from textual.containers import Container
from src.utils.database import Database
from src.utils.constants import TASK_CONTAINER_ID

class TaskContainer(Container):
    def __init__(self, database: Database):
        super().__init__(id=TASK_CONTAINER_ID)
        self.database = database
        self.border_title = f"Project {self.database.project_name}"

    def compose(self) -> ComposeResult:
        yield Tasks(database=self.database)
    
    def on_mount(self):
        """Focus the search input when container is mounted"""
        self.query_one("#tasks").focus()
