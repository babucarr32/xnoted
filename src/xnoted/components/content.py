from textual.widgets import Static
from xnoted.components.body import Body
from xnoted.components.taskContainer import TaskContainer
from textual.containers import Vertical
from textual.app import ComposeResult
from typing import Iterator
from xnoted.components.taskHeader import TaskHeader
from xnoted.database.dataProvider import DataProvider
from xnoted.config.manager import ConfigHandler


class Content(Static):
    def __init__(self, data_provider: DataProvider, config_handler: ConfigHandler):
        super().__init__()
        self.data_provider = data_provider
        self.config_handler = config_handler

    def compose(self) -> ComposeResult:
        yield Vertical(
            TaskHeader(data_provider=self.data_provider),
            TaskContainer(
                data_provider=self.data_provider, config_handler=self.config_handler
            ),
        )
        yield Body(data_provider=self.data_provider, config_handler=self.config_handler)

    def on_mount(self) -> None:
        # Show welcome screen
        if self.data_provider.is_empty():
            body_widget: Body = self.app.query_one(Body)
            body_widget.welcome()


class ContentWrapper(Static):
    def __init__(self, data_provider: DataProvider, config_handler: ConfigHandler):
        super().__init__()
        self.data_provider = data_provider
        self.config_handler = config_handler

    def compose(self) -> Iterator[Content]:
        yield Content(
            data_provider=self.data_provider, config_handler=self.config_handler
        )
