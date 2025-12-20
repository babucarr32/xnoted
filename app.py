from textual.app import App
from src.screens.createTodo import CreateToDoModal
from src.components.content import ContentWrapper
from src.components.body import Body


class TodoCLIApp(App):
    CSS_PATH = "src/styles/main.tcss"
    BINDINGS = [
        ("ctrl+n", "create_new_todo", "Create new todo"),
        ("ctrl+d", "scroll_body_down", "Scroll body down"),
        ("ctrl+u", "scroll_body_up", "Scroll body up"),
    ]

    def compose(self):
        yield ContentWrapper()

    def action_create_new_todo(self):
        self.app.push_screen(CreateToDoModal())

    def action_scroll_body_down(self):
        body_widget = self.app.query_one(Body)
        body_widget.scroll_down()

    def action_scroll_body_up(self):
        body_widget = self.app.query_one(Body)
        body_widget.scroll_up()
