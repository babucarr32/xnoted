from xnoted.components.tasks import Tasks
from textual.app import ComposeResult
from textual.containers import Container
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import TASK_CONTAINER_ID

class TaskContainer(Container):
    def __init__(self, data_provider: DataProvider):
        super().__init__(id=TASK_CONTAINER_ID)
        self.data_provider = data_provider
        self.border_title = "Tasks"

    def compose(self) -> ComposeResult:
        yield Tasks(data_provider=self.data_provider)
    
    def on_mount(self) -> None:
        """Focus the search input when container is mounted"""
        self.query_one("#tasks").focus()
