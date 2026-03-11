from typing import Iterator
from textual.widgets import Static, Label
from xnoted.database.dataProvider import DataProvider
from xnoted.utils.constants import TASK_HEADER_ID


class TaskHeader(Static):
    BORDER_TITLE = "Project"

    def __init__(self, data_provider: DataProvider):
        super().__init__()
        self.data_provider = data_provider

    def compose(self) -> Iterator[Label]:
        yield Label(self.data_provider.project_name, id=TASK_HEADER_ID)
