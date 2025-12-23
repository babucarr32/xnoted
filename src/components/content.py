from textual.widgets import Static
from src.components.body import Body
from src.components.todoContainer import TodoContainer
from textual.containers import Container


class Content(Static):
    def compose(self):
        yield Container(TodoContainer())
        yield Body()

class ContentWrapper(Static):
    def compose(self):
        yield Content()
