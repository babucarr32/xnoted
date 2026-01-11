from textual.widgets import Static


class CustomHeader(Static):
    def compose(self):
        yield Static("Welcom To XNoted", classes="customHeader")
