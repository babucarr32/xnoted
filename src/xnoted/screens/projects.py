from textual.screen import ModalScreen
from collections.abc import Callable
from textual.app import ComposeResult
from textual.widgets import Label, ListView, ListItem
from xnoted.database.dataProvider import DataProvider
from typing import cast
from xnoted.utils.helpers import slugify
from xnoted.screens.createProject import CreateProjectModal
from xnoted.screens.confirm import ConfirmModal
from xnoted.utils.constants import PROJECTS_ID, TASK_HEADER_ID, TASKS_ID
from xnoted.components.tasks import Tasks
from xnoted.config.manager import ConfigHandler


class ProjectItem(ListItem):
    def __init__(
        self, *args, project_id: str = "", project_name: str = "", **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.project_name = project_name


class ProjectsModal(ListView):
    def __init__(
        self,
        data_provider: DataProvider,
        close_app: Callable[[], None],
        config_handler: ConfigHandler,
    ):
        super().__init__(id=PROJECTS_ID)
        self.has_task_result = True
        self.data_provider = data_provider
        self.close_app = close_app
        self.config_handler = config_handler

    BORDER_TITLE = "Projects"

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.project_list

        self._bindings.bind(
            keys=kb.cursor_up, action="cursor_up", description="Cursor up"
        )
        self._bindings.bind(
            keys=kb.cursor_down, action="cursor_down", description="Cursor down"
        )
        self._bindings.bind(
            keys=kb.edit_project, action="edit_project", description="Cursor down"
        )
        self._bindings.bind(
            keys=kb.delete_project, action="delete_project", description="Cursor down"
        )
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
                on_submit=lambda: self.load_projects(),
                project_id=project_id,
                config_handler=self.config_handler,
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

        self.app.push_screen(
            ConfirmModal(on_confirm=on_confirm, config_handler=self.config_handler)
        )


class SelectProjectModal(ModalScreen):
    def __init__(self, data_provider: DataProvider, config_handler: ConfigHandler):
        self.data_provider = data_provider
        super().__init__()
        self.config_handler = config_handler

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(keys=kb.cancel, action="close", description="Close modal")

    def compose(self) -> ComposeResult:
        yield ProjectsModal(
            data_provider=self.data_provider,
            close_app=self.action_close,
            config_handler=self.config_handler,
        )

    def action_close(self) -> None:
        self.app.pop_screen()
