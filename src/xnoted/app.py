from textual.app import App
from textual import work
from xnoted.screens.createTask import CreateTaskModal
from xnoted.screens.projects import SelectProjectModal
from xnoted.screens.createProject import CreateProjectModal
from xnoted.screens.importExportProject import ImportExportProjectModal
from xnoted.components.content import ContentWrapper
from xnoted.errors.errorHandler import ErrorHandler
from xnoted.components.footer import Footer
from xnoted.screens.enterPassword import EnterPasswordModal
from xnoted.screens.syncConfig import SyncConfigModal
from xnoted.screens.createPassword import CreatePasswordModal
from xnoted.screens.editPassword import EditPasswordModal
from xnoted.screens.commandPalette import CommandPaletteModal
from xnoted.components.body import Body
from xnoted.database.dataProvider import DataProvider
from xnoted.database.sqlDataHandler import SqlDataHandler
from xnoted.components.spinner import Spinner
from typing import Iterator, cast
from xnoted.action.pullSync import pull_sync
from xnoted.action.pushSync import push_sync
from xnoted.sync.syncProvider import SyncProvider
from xnoted.utils.keyringService import DBKeyring
from xnoted.sync.mongodbSyncHandler import MongoDBSyncHandler
from xnoted.config.manager import ConfigHandler


class XNotedApp(App):
    def __init__(self) -> None:
        super().__init__()
        self.config_handler = ConfigHandler()
        self.db_keyring = DBKeyring()
        self.sql_data_handler = SqlDataHandler()
        self.data_provider = DataProvider(self.sql_data_handler)
        mongo_db_sync_handler = MongoDBSyncHandler(keyring=self.db_keyring)
        self.sync = SyncProvider(sync=mongo_db_sync_handler)

    CSS_PATH = "styles/main.tcss"

    def on_mount(self):
        config = self.config_handler.get()
        kb = config.keybindings.global_

        self.bind(
            keys=kb.create_task, action="create_new_task", description="Create new task"
        )
        self.bind(
            keys=kb.select_project,
            action="select_project",
            description="Select project",
        )
        self.bind(
            keys=kb.import_export,
            action="import_export_project",
            description="Import or Export project",
        )
        self.bind(
            keys=kb.create_project,
            action="create_new_project",
            description="Create project",
        )
        self.bind(
            keys=kb.scroll_down,
            action="scroll_body_down",
            description="Scroll body down",
        )
        self.bind(
            keys=kb.scroll_up, action="scroll_body_up", description="Scroll body up"
        )
        self.bind(keys=kb.pull_sync, action="pull_sync", description="Pull sync data")
        self.bind(
            keys=kb.config_sync, action="config_sync", description="Config sync data"
        )
        self.bind(keys=kb.push_sync, action="push_sync", description="Push sync data")
        self.bind(
            keys=kb.edit_password,
            action="create_password",
            description="Create or edit password",
        )
        self.bind(
            keys=kb.unlock_tasks,
            action="unlock_password",
            description="Unlock password",
        )
        self.bind(keys=kb.show_readme, action="show_readme", description="Show readme")

    def compose(self) -> Iterator[ContentWrapper | Footer]:
        yield ContentWrapper(
            data_provider=self.data_provider, config_handler=self.config_handler
        )
        yield Footer(
            data_provider=self.data_provider, config_handler=self.config_handler
        )

    def action_create_new_task(self) -> None:
        self.app.push_screen(
            CreateTaskModal(
                data_provider=self.data_provider, config_handler=self.config_handler
            )
        )

    @work(exclusive=True)
    async def action_pull_sync(self) -> None:
        try:
            spinner = cast(Spinner, self.app.query_one(Spinner))
            await spinner.wrap(
                pull_sync(sync=self.sync, data_provider=self.data_provider),
                "Pulling...",
            )
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    @work(exclusive=True)
    async def action_push_sync(self) -> None:
        try:
            spinner = cast(Spinner, self.app.query_one(Spinner))
            await spinner.wrap(
                push_sync(sync=self.sync, data_provider=self.data_provider),
                "Pushing...",
            )
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def action_create_new_project(self) -> None:
        self.app.push_screen(
            CreateProjectModal(
                data_provider=self.data_provider,
                on_submit=lambda: None,
                config_handler=self.config_handler,
            )
        )

    def action_create_password(self) -> None:
        def on_password_created():
            pass

        if self.data_provider.is_password_set:
            self.app.push_screen(
                EditPasswordModal(
                    data_provider=self.data_provider, config_handler=self.config_handler
                )
            )
            return

        self.app.push_screen(
            CreatePasswordModal(
                data_provider=self.data_provider,
                on_password_created=on_password_created,
                config_handler=self.config_handler,
            )
        )

    def action_config_sync(self) -> None:
        self.app.push_screen(
            SyncConfigModal(
                data_provider=self.data_provider, config_handler=self.config_handler
            )
        )

    def action_import_export_project(self) -> None:
        self.app.push_screen(
            ImportExportProjectModal(
                data_provider=self.data_provider, config_handler=self.config_handler
            )
        )

    def action_select_project(self) -> None:
        self.app.push_screen(
            SelectProjectModal(
                data_provider=self.data_provider, config_handler=self.config_handler
            )
        )

    def action_command_palette(self) -> None:
        bindings = self.app.active_bindings
        self.app.push_screen(
            CommandPaletteModal(bindings=bindings, config_handler=self.config_handler)
        )

    def action_unlock_password(self) -> None:
        def refresh_tasks():
            from xnoted.components.tasks import Tasks
            from xnoted.utils.constants import TASKS_ID

            tasks_widget = cast(Tasks, self.query_one(f"#{TASKS_ID}"))
            tasks_widget.load_tasks()

        if self.data_provider.is_data_unprotected:
            self.data_provider.is_data_unprotected = False
            refresh_tasks()
            return

        self.data_provider.is_data_unprotected = True
        self.app.push_screen(
            EnterPasswordModal(
                data_provider=self.data_provider,
                on_password_valid=refresh_tasks,
                config_handler=self.config_handler,
            )
        )

    def action_scroll_body_down(self) -> None:
        body_widget: Body = self.app.query_one(Body)
        body_widget.scroll_down()

    def action_show_readme(self) -> None:
        body_widget: Body = self.app.query_one(Body)
        body_widget.welcome()

    def action_scroll_body_up(self) -> None:
        body_widget = self.app.query_one(Body)
        body_widget.scroll_up()
