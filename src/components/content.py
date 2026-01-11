from textual.widgets import Static
from src.components.body import Body
from src.components.taskContainer import TaskContainer
from textual.containers import Container
from src.utils.database import Database


class Content(Static):
    def __init__(self, database: Database):
        super().__init__()
        self.database = database

    def compose(self):
        yield Container(TaskContainer(database=self.database))
        yield Body(database=self.database)

class ContentWrapper(Static):
    def __init__(self, database: Database):
        super().__init__()
        self.database = database

    def compose(self):
        yield Content(database=self.database)
