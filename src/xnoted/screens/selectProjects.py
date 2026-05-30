from typing import Iterator
from textual.screen import ModalScreen
from collections.abc import Callable
from textual.widgets import Label, ListView, ListItem
from xnoted.database.dataProvider import DataProvider
from typing import cast, Any
from xnoted.utils.helpers import slugify
from xnoted.utils.constants import PROJECTS_ID
from xnoted.config.manager import ConfigHandler


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
        config_handler: ConfigHandler,
        on_select: Callable[[str], None],
        close_on_select: bool,
        border_title: str,
    ):
        super().__init__(id=PROJECTS_ID)
        self.has_task_result = True
        self.data_provider = data_provider
        self.close_app = close_app
        self.config_handler = config_handler
        self.on_select = on_select
        self.close_on_select = close_on_select
        self.border_title = border_title

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.project_list

        self._bindings.bind(
            keys=kb.cursor_up, action="cursor_up", description="Cursor up"
        )
        self._bindings.bind(
            keys=kb.cursor_down, action="cursor_down", description="Cursor down"
        )
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
            return

        self.append(ListItem(Label("No projects yet")))

    def on_list_view_selected(self, event: ListView.Highlighted) -> None:
        item = cast(ProjectItem, event.item)
        if not item:
            return

        self.on_select(item.project_id)
        if self.close_on_select:
            self.close_app()


class SelectProjectModal(ModalScreen):
    def __init__(
        self,
        data_provider: DataProvider,
        on_select: Callable[[str], None],
        config_handler: ConfigHandler,
        _border_title: str = "Select project",
    ):
        super().__init__()
        self.data_provider = data_provider
        self.on_select = on_select
        self.config_handler = config_handler
        self._border_title: Any = _border_title

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form
        print('----------', kb)

        self._bindings.bind(keys=kb.cancel, action="close", description="Close modal")

    def compose(self) -> Iterator[SelectProject]:
        yield SelectProject(
            data_provider=self.data_provider,
            config_handler=self.config_handler,
            close_app=self.action_close,
            close_on_select=True,
            on_select=self.on_select,
            border_title=self._border_title,
        )

    def action_close(self) -> None:
        self.app.pop_screen()
