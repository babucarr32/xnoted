from textual.widgets import Static
from xnoted.components.body import Body
from xnoted.components.taskContainer import TaskContainer
from textual.containers import Vertical
from textual.app import ComposeResult
from typing import Iterator
from xnoted.components.taskHeader import TaskHeader
from xnoted.database.dataProvider import DataProvider


class Content(Static):
    def __init__(self, data_provider: DataProvider):
        super().__init__()
        self.data_provider = data_provider

    def compose(self) -> ComposeResult:
        yield Vertical(
            TaskHeader(data_provider=self.data_provider),
            TaskContainer(data_provider=self.data_provider),
        )
        yield Body(data_provider=self.data_provider)

    def on_mount(self) -> None:
        # Show welcome screen
        if self.data_provider.is_empty():
            body_widget: Body = self.app.query_one(Body)
            body_widget.welcome()

class ContentWrapper(Static):
    def __init__(self, data_provider: DataProvider):
        super().__init__()
        self.data_provider = data_provider

    def compose(self) -> Iterator[Content]:
        yield Content(data_provider=self.data_provider)
