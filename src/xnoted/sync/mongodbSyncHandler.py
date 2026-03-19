from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from typing import TypedDict, Callable, Dict, Any, TypeVar, Generic, Awaitable
from xnoted.sync.syncProvider import Project, Task, PullResult
from xnoted.utils.constants import MONGO_URI, DATABASE_NAME
from xnoted.sync.syncProvider import SyncStatus
from xnoted.database.dataHelper import DataHelper
from dataclasses import dataclass

PROJECTS_DOCUMENT = "projects"
TASK_DOCUMENT = "tasks"
T = TypeVar("T")


@dataclass(frozen=True)
class DataFilter(Generic[T]):
    added: list[T]
    removed: list[T]
    pending_edit: list[T]


class DeleteProject(TypedDict):
    project_id: str


class DeleteTask(TypedDict):
    task_id: str


dataHelper = DataHelper()


class MongoDBSyncHandler:
    def __init__(self) -> None:
        self.uri = MONGO_URI
        self.client: AsyncMongoClient | None = None
        self.database: AsyncDatabase | None = None

    async def initialize(self) -> None:
        print("Connecting to database...")

        self.client = AsyncMongoClient(self.uri)
        self.database = self.client[DATABASE_NAME]

        print("Connected successfully")

    async def _handle_find_all(
        self, document_name: str, helper: Callable[[Dict[str, Any]], T]
    ) -> list[T] | None:
        if self.database is None:
            return None

        cursor = self.database[document_name].find()
        results: list[T] = []

        async for doc in cursor:
            results.append(helper(doc))

        return results

    async def _get_projects(self) -> list[Project] | None:
        def get_data(data: Dict[str, Any]):
            return dataHelper.dict_to_sync_project(data, project_id_key="project_id")

        return await self._handle_find_all(PROJECTS_DOCUMENT, get_data)

    async def _get_tasks(self) -> list[Task] | None:
        def get_data(data: Dict[str, Any]):
            return dataHelper.dict_to_sync_task(data, task_id_key="task_id")

        return await self._handle_find_all(TASK_DOCUMENT, helper=get_data)

    async def _handle_insert_task(self, data: Task) -> None:
        if self.database is None:
            return

        tasks = self.database[TASK_DOCUMENT]
        updated_data = data.to_dict()
        updated_data["sync_status"] = SyncStatus.SYNCED.value
        await tasks.insert_one(updated_data)

    async def _handle_delete_task(self, data: Task) -> None:
        if self.database is None:
            return

        tasks = self.database[TASK_DOCUMENT]
        await tasks.delete_one(DeleteTask(task_id=data.task_id))

    async def _handle_delete_tasks(self, data: list[Task]) -> None:
        if self.database is None:
            return

        tasks = self.database[TASK_DOCUMENT]

        task_ids = [t.task_id for t in data]

        await tasks.delete_many({"task_id": {"$in": task_ids}})

    async def _handle_insert_project(self, data: Project) -> None:
        if self.database is None:
            return

        projects = self.database[PROJECTS_DOCUMENT]
        updated_data = data.to_dict()
        updated_data["sync_status"] = SyncStatus.SYNCED.value
        await projects.insert_one(updated_data)

    async def _handle_delete_project(self, data: Project) -> None:
        if self.database is None:
            return

        projects = self.database[PROJECTS_DOCUMENT]
        await projects.delete_one(DeleteProject(project_id=data.project_id))

    async def _handle_delete_projects(self, data: list[Project]) -> None:
        if self.database is None:
            return

        for project in data:
            await self._handle_delete_project(project)

    async def _handle_insert_projects(self, data: list[Project]) -> None:
        if self.database is None:
            return

        projects_collection = self.database[PROJECTS_DOCUMENT]
        if len(data):
            updated_data: list[dict] = []
            for p in data:
                p_dict = p.to_dict()
                p_dict["sync_status"] = SyncStatus.SYNCED.value
                updated_data.append(p_dict)

            await projects_collection.insert_many(updated_data)

    async def _handle_update_projects(self, data: list[Project]) -> None:
        if self.database is None:
            return

        if len(data):
            for p in data:
                await self._handle_update_project(p)

    async def _handle_update_tasks(self, data: list[Task]) -> None:
        if self.database is None:
            return

        if len(data):
            for p in data:
                await self._handle_update_task(p)

    async def _handle_update_project(self, data: Project) -> None:
        if self.database is None:
            return

        projects_collection = self.database[PROJECTS_DOCUMENT]

        p_dict = data.to_dict()
        p_dict["sync_status"] = SyncStatus.SYNCED.value

        await projects_collection.find_one_and_update(
            {"project_id": data.project_id}, {"$set": p_dict}
        )

    async def _handle_update_task(self, data: Task) -> None:
        if self.database is None:
            return

        tasks_collection = self.database[TASK_DOCUMENT]

        t_dict = data.to_dict()
        t_dict["sync_status"] = SyncStatus.SYNCED.value

        await tasks_collection.find_one_and_update(
            {"task_id": data.task_id}, {"$set": t_dict}
        )

    async def _handle_insert_tasks(self, data: list[Task]) -> None:
        if self.database is None:
            return

        tasks_collection = self.database[TASK_DOCUMENT]
        if len(data):
            updated_data: list[dict] = []
            for t in data:
                t_dict = t.to_dict()
                t_dict["sync_status"] = SyncStatus.SYNCED.value
                updated_data.append(t_dict)

            await tasks_collection.insert_many(updated_data)

    async def _handle_filter_data(
        self,
        local_data: list[T],
        get_remote_data_handler: Callable[[], Awaitable[list[T] | None]],
        get_id: Callable[[T], str],
        get_sync_status: Callable[[T], str],
    ) -> DataFilter[T] | None:
        if self.database is None:
            return None

        remote_data = await get_remote_data_handler()
        if not remote_data:
            return DataFilter(added=local_data, removed=[], pending_edit=[])

        remote_by_id = {get_id(p): p for p in remote_data}
        local_by_id = {get_id(p): p for p in local_data}

        added: list[T] = []
        removed: list[T] = []
        pending_edit: list[T] = []

        # Pending edit
        for d_id, d in local_by_id.items():
            if get_sync_status(d) == SyncStatus.PENDING_EDIT.value:
                pending_edit.append(d)

        # Removed
        for d_id, d in remote_by_id.items():
            if (
                d_id not in local_by_id
                and get_sync_status(d) == SyncStatus.SYNCED.value
            ):
                removed.append(d)

        # Added
        for d_id, d in local_by_id.items():
            if (
                d_id not in remote_by_id
                and get_sync_status(d) == SyncStatus.PENDING.value
            ):
                added.append(d)

        return DataFilter(added=added, removed=removed, pending_edit=pending_edit)

    async def _handle_filter_projects(
        self, data: list[Project]
    ) -> DataFilter[Project] | None:
        return await self._handle_filter_data(
            local_data=data,
            get_remote_data_handler=self._get_projects,
            get_id=lambda d: d.project_id,
            get_sync_status=lambda d: d.sync_status or "",
        )

    async def _handle_filter_tasks(self, data: list[Task]) -> DataFilter[Task] | None:
        return await self._handle_filter_data(
            local_data=data,
            get_remote_data_handler=self._get_tasks,
            get_id=lambda d: d.task_id,
            get_sync_status=lambda d: d.sync_status or "",
        )

    async def push(self, projects: list[Project]) -> None:
        if self.database is None:
            return

        if not projects:
            return

        filtered_project = await self._handle_filter_projects(projects)

        if not filtered_project:
            return None

        await self._handle_delete_projects(filtered_project.removed)
        await self._handle_insert_projects(filtered_project.added)
        await self._handle_update_projects(filtered_project.pending_edit)

    async def push_tasks(self, tasks: list[Task]) -> None:
        if self.database is None:
            return

        if not tasks:
            return

        filtered_task = await self._handle_filter_tasks(tasks)

        if not filtered_task:
            return None

        await self._handle_delete_tasks(filtered_task.removed)
        await self._handle_insert_tasks(filtered_task.added)
        await self._handle_update_tasks(filtered_task.pending_edit)

    async def pull(self) -> PullResult:
        projects = await self._get_projects()
        tasks = await self._get_tasks()

        return PullResult(
            projects=projects or [],
            tasks=tasks or [],
        )

    async def close(self) -> None:
        if self.client:
            await self.client.close()
