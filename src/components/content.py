from textual.widgets import Static
from src.components.todos import Todos
from src.components.customHeader import CustomHeader
from src.components.body import Body

class Content(Static):
    def compose(self):
        yield Todos()
        yield Body()

class ContentWrapper(Static):
    def compose(self):
        yield CustomHeader()
        yield Content()
