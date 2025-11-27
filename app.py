from textual.app import App
from src.components.content import ContentWrapper

class TodoCLIApp(App):
    CSS_PATH = "src/styles/main.tcss"

    def compose(self):
        yield ContentWrapper()
