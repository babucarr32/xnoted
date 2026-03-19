from textual.app import App
from xnoted.screens.createTask import CreateTaskModal
from xnoted.screens.projects import SelectProjectModal
from xnoted.screens.createProject import CreateProjectModal
from xnoted.sync.syncProvider import SyncStatus
from xnoted.screens.importExportProject import ImportExportProjectModal
from xnoted.components.content import ContentWrapper
from xnoted.components.footer import Footer
from xnoted.screens.enterPassword import EnterPasswordModal
from xnoted.components.body import Body
from xnoted.database.dataProvider import DataProvider, Task, Project
from xnoted.database.sqlDataHandler import SqlDataHandler
from typing import Iterator, cast
from xnoted.sync.syncProvider import SyncProvider
from xnoted.sync.mongodbSyncHandler import MongoDBSyncHandler
from xnoted.sync.syncProvider import Project as SyncProject
from xnoted.sync.syncProvider import Task as SyncTask


class XNotedApp(App):
    def __init__(self) -> None:
        super().__init__()
        self.sqlDataHandler = SqlDataHandler()
        self.data_provider = DataProvider(self.sqlDataHandler)
        mongoDBSyncHandler = MongoDBSyncHandler()
        self.sync = SyncProvider(sync=mongoDBSyncHandler)

    CSS_PATH = "styles/main.tcss"
    BINDINGS = [
        ("ctrl+n", "create_new_task", "Create new task"),
        ("ctrl+l", "select_project", "Select project"),
        ("ctrl+o", "import_export_project", "Import or Export project"),
        ("ctrl+b", "create_new_project", "Create project"),
        ("ctrl+d", "scroll_body_down", "Scroll body down"),
        ("ctrl+u", "scroll_body_up", "Scroll body up"),
        ("p", "pull_sync", "Pull sync data"),
        ("P", "push_sync", "Push sync data"),
        ("u", "unlock_password", "Unlock password"),
        ("ctrl+r", "show_readme", "Show readme"),
    ]

    def compose(self) -> Iterator[ContentWrapper | Footer]:
        yield ContentWrapper(data_provider=self.data_provider)
        yield Footer(data_provider=self.data_provider)

    def action_create_new_task(self) -> None:
        self.app.push_screen(CreateTaskModal(data_provider=self.data_provider))

    async def action_pull_sync(self) -> None:
        await self.sync.initialize()
        pull_result = await self.sync.pull()

        incoming_tasks = [
            Task(
                id=t.task_id,
                title=t.title,
                content=t.content,
                project_id=t.project_id,
                status=t.status,
                is_protected=t.is_protected,
                createdAt=t.createdAt,
                sync_status=t.sync_status,
            )
            for t in pull_result.tasks
        ]

        incoming_projects = [
            Project(
                id=p.project_id,
                title=p.title,
                description=p.description,
                type=p.type,
                createdAt=p.createdAt,
                sync_status=p.sync_status,
            )
            for p in pull_result.projects
        ]

        self.data_provider.sync(
            incoming_tasks,
            incoming_projects,
        )

    async def action_push_sync(self) -> None:
        await self.sync.initialize()
        projects = self.data_provider.load_projects()

        # Push projects
        await self.sync.push(
            [
                SyncProject(
                    title=p.title,
                    description=p.description,
                    type=p.type,
                    createdAt=p.createdAt,
                    sync_status=p.sync_status,
                    project_id=p.id,
                )
                for p in projects
            ]
        )

        # Update status on sync success
        for project in projects:
            if project.sync_status == SyncStatus.PENDING.value:
                self.data_provider.update_project(
                    project.id,
                    Project(
                        id=project.id,
                        title=project.title,
                        description=project.description,
                        type=project.type,
                        createdAt=project.createdAt,
                        sync_status=SyncStatus.SYNCED.value,
                    ),
                )

        # Push tasks
        tasks: list[Task] = []
        for p in projects:
            tasks = [*tasks, *self.data_provider.load_tasks(p.id)]

        await self.sync.push_tasks(
            [
                SyncTask(
                    task_id=p.id,
                    project_id=p.project_id,
                    title=p.title,
                    content=p.content,
                    is_protected=p.is_protected,
                    status=p.status,
                    createdAt=p.createdAt,
                    sync_status=p.sync_status,
                )
                for p in tasks
            ]
        )

        # Update status on sync success
        for task in tasks:
            if task.sync_status == SyncStatus.PENDING.value:
                self.data_provider.update_task(
                    task.id,
                    Task(
                        id=task.id,
                        project_id=task.project_id,
                        title=task.title,
                        content=task.content,
                        is_protected=task.is_protected,
                        status=task.status,
                        createdAt=task.createdAt,
                        sync_status=SyncStatus.SYNCED.value,
                    ),
                )

    def action_create_new_project(self) -> None:
        self.app.push_screen(CreateProjectModal(data_provider=self.data_provider))

    def action_import_export_project(self) -> None:
        self.app.push_screen(ImportExportProjectModal(data_provider=self.data_provider))

    def action_select_project(self) -> None:
        self.app.push_screen(SelectProjectModal(data_provider=self.data_provider))

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
                data_provider=self.data_provider, on_password_valid=refresh_tasks
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
