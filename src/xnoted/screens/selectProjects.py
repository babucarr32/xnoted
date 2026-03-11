from typing import Iterator
from textual.screen import ModalScreen
from collections.abc import Callable
from textual.widgets import Label, ListView, ListItem
from xnoted.database.dataProvider import DataProvider
from textual.binding import Binding
from typing import cast, Any
from xnoted.utils.helpers import slugify
from xnoted.utils.constants import PROJECTS_ID


class ProjectItem(ListItem):
    def __init__(
        self, *args, project_id: str = "", project_name: str = "", **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.project_id = project_id
        self.project_name = project_name


class SelectProject(ListView):
    def __init__(
        self,
        data_provider: DataProvider,
        close_app: Callable[[], None],
        on_select: Callable[[str], None],
        close_on_select: bool,
        border_title: str,
    ):
        super().__init__(id=PROJECTS_ID)
        self.has_task_result = True
        self.data_provider = data_provider
        self.close_app = close_app
        self.on_select = on_select
        self.close_on_select = close_on_select
        self.border_title = border_title

    BINDINGS = [
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
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
                list_item = ProjectItem(
                    Label(f"{title}"),
                    project_id=project_id,
                    project_name=slugify(title),
                )
                self.append(list_item)
        else:
            self.append(ListItem(Label("No projects yet")))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = cast(ProjectItem, event.item)
        if item:
            self.on_select(item.project_id)
            if self.close_on_select:
                self.close_app()


class SelectProjectModal(ModalScreen):
    def __init__(
        self,
        data_provider: DataProvider,
        on_select: Callable[[str], None],
        _border_title: str = "Select project",
    ):
        super().__init__()
        self.data_provider = data_provider
        self.on_select = on_select
        self._border_title: Any = _border_title

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> Iterator[SelectProject]:
        yield SelectProject(
            data_provider=self.data_provider,
            close_app=self.action_close,
            close_on_select=True,
            on_select=self.on_select,
            border_title=self._border_title,
        )

    def action_close(self) -> None:
        self.app.pop_screen()
