from textual.app import App
from src.screens.createTodo import CreateToDoModal
from src.screens.projects import SelectProjectModal
from src.screens.createProject import CreateProjectModal
from src.components.content import ContentWrapper
from src.components.body import Body
from src.utils.database import Database


class TodoCLIApp(App):
    def __init__(self):
        super().__init__()
        self.database = Database()

    CSS_PATH = "src/styles/main.tcss"
    BINDINGS = [
        ("ctrl+n", "create_new_todo", "Create new todo"),
        ("ctrl+l", "select_project", "Select project"),
        ("ctrl+b", "create_new_project", "Create project"),
        ("ctrl+d", "scroll_body_down", "Scroll body down"),
        ("ctrl+u", "scroll_body_up", "Scroll body up"),
    ]

    def compose(self):
        yield ContentWrapper(database=self.database)

    def action_create_new_todo(self):
        self.app.push_screen(CreateToDoModal(database=self.database))

    def action_create_new_project(self):
        self.app.push_screen(CreateProjectModal(database=self.database))

    def action_select_project(self):
        self.app.push_screen(SelectProjectModal(database=self.database))

    def action_scroll_body_down(self):
        body_widget = self.app.query_one(Body)
        body_widget.scroll_down()

    def action_scroll_body_up(self):
        body_widget = self.app.query_one(Body)
        body_widget.scroll_up()
