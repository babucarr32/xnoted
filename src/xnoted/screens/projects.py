from textual.screen import ModalScreen
from collections.abc import Callable
from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem
from xnoted.database.dataProvider import DataProvider
from textual.binding import Binding
from typing import cast
from xnoted.utils.helpers import slugify
from xnoted.screens.createProject import CreateProjectModal
from xnoted.screens.confirm import ConfirmModal
from xnoted.utils.constants import PROJECTS_ID, TASK_HEADER_ID, TASKS_ID
from xnoted.components.tasks import Tasks


class ProjectItem(ListItem):
    def __init__(
        self, *args, project_id: str = "", project_name: str = "", **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.project_name = project_name


class Projects(ListView):
    def __init__(self, data_provider: DataProvider, close_app: Callable[[], None]):
        super().__init__(id=PROJECTS_ID)
        self.has_task_result = True
        self.data_provider = data_provider
        self.close_app = close_app

    BORDER_TITLE = "Projects"
    BINDINGS = [
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
        Binding("e", "edit_project", "Cursor down", show=False),
        Binding("d", "delete_project", "Cursor down", show=False),
    ]

    def on_mount(self) -> None:
        self.load_projects()

    def load_projects(self) -> None:
        self.clear()
        projects = self.data_provider.load_projects()

        if projects:
            for project in projects:
                title = project.title
                project_id = project.id
                list_item = ProjectItem(Label(f"{title}"))
                list_item.project_id = project_id
                list_item.project_name = slugify(title)
                self.append(list_item)
            return

        self.append(ListItem(Label("No projects yet")))

    def on_list_view_selected(self, event: ListView.Highlighted) -> None:
        project_id = cast(ProjectItem, event.item).project_id
        self.data_provider.set_current_project(project_id)
        tasks_widget = cast(Tasks, self.app.query_one(f"#{TASKS_ID}"))
        tasks_widget.refresh_tasks()
        task_header_label_widget = cast(Label, self.app.query_one(f"#{TASK_HEADER_ID}"))
        task_header_label_widget.update(self.data_provider.project_name)
        self.close_app()

    def action_edit_project(self) -> None:
        child = cast(ProjectItem | None, self.highlighted_child)

        if not child or not hasattr(child, "project_id"):
            return

        project_id = child.project_id
        project = self.data_provider.get_project(project_id)

        if not project:
            return None

        self.app.push_screen(
            CreateProjectModal(
                data_provider=self.data_provider,
                editing=True,
                project_id=project_id,
                project_type=project.type,
            )
        )

    def action_delete_project(self) -> None:
        child = cast(ProjectItem | None, self.highlighted_child)

        if not child or not hasattr(child, "project_id"):
            return

        project_id = child.project_id

        def on_confirm():
            self.data_provider.delete_project(project_id)
            first_project = self.data_provider.get_first_project()
            self.data_provider.set_current_project(first_project.id)
            self.load_projects()
            tasks_widget = self.app.query_one(f"#{TASKS_ID}")
            tasks_widget.refresh_tasks()

        self.app.push_screen(ConfirmModal(on_confirm=on_confirm))


class SelectProjectModal(ModalScreen):
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        super().__init__()

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> ComposeResult:
        yield Projects(data_provider=self.data_provider, close_app=self.action_close)

    def action_close(self) -> None:
        self.app.pop_screen()
