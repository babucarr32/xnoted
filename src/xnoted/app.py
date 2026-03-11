from textual.app import App
from xnoted.screens.createTask import CreateTaskModal
from xnoted.screens.projects import SelectProjectModal
from xnoted.screens.createProject import CreateProjectModal
from xnoted.screens.importExportProject import ImportExportProjectModal
from xnoted.components.content import ContentWrapper
from xnoted.components.footer import Footer
from xnoted.components.body import Body
from xnoted.database.dataProvider import DataProvider
from xnoted.database.sqlDataHandler import SqlDataHandler
from typing import Iterator


class XNotedApp(App):
    def __init__(self) -> None:
        super().__init__()
        self.sqlDataHandler = SqlDataHandler()
        self.data_provider = DataProvider(self.sqlDataHandler)

    CSS_PATH = "styles/main.tcss"
    BINDINGS = [
        ("ctrl+n", "create_new_task", "Create new task"),
        ("ctrl+l", "select_project", "Select project"),
        ("ctrl+o", "import_export_project", "Import or Export project"),
        ("ctrl+b", "create_new_project", "Create project"),
        ("ctrl+d", "scroll_body_down", "Scroll body down"),
        ("ctrl+u", "scroll_body_up", "Scroll body up"),
        ("ctrl+r", "show_readme", "Show readme"),
    ]

    def compose(self) -> Iterator[ContentWrapper | Footer]:
        yield ContentWrapper(data_provider=self.data_provider)
        yield Footer(data_provider=self.data_provider)

    def action_create_new_task(self) -> None:
        self.app.push_screen(CreateTaskModal(data_provider=self.data_provider))

    def action_create_new_project(self) -> None:
        self.app.push_screen(CreateProjectModal(data_provider=self.data_provider))

    def action_import_export_project(self) -> None:
        self.app.push_screen(ImportExportProjectModal(data_provider=self.data_provider))

    def action_select_project(self) -> None:
        self.app.push_screen(SelectProjectModal(data_provider=self.data_provider))

    def action_scroll_body_down(self) -> None:
        body_widget: Body = self.app.query_one(Body)
        body_widget.scroll_down()

    def action_show_readme(self) -> None:
        body_widget: Body = self.app.query_one(Body)
        body_widget.welcome()

    def action_scroll_body_up(self) -> None:
        body_widget = self.app.query_one(Body)
        body_widget.scroll_up()
