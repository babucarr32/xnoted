from textual.widgets import Static

class CustomHeader(Static):
    def compose(self):
        yield Static("Welcom To Todo CLI", classes="customHeader")

