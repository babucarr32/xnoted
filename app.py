from textual.app import App
from src.screens.createTodo import CreateToDoModal
from src.components.content import ContentWrapper


class TodoCLIApp(App):
    CSS_PATH = "src/styles/main.tcss"
    BINDINGS = [
        ("ctrl+n", "create_new_todo", "Create new todo"),
    ]

    def compose(self):
        yield ContentWrapper()

    def action_create_new_todo(self):
        self.app.push_screen(CreateToDoModal())
