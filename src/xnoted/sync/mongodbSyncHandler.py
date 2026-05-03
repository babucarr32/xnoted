from pymongo import AsyncMongoClient
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError
from pymongo.asynchronous.database import AsyncDatabase
from typing import (
    TypedDict,
    Callable,
    Dict,
    Any,
    TypeVar,
    Generic,
    Awaitable,
    cast,
)
from xnoted.sync.syncProvider import Project, Task, PullResult, Account
from xnoted.sync.syncProvider import SyncStatus
from xnoted.utils.keyringService import DBKeyring
from xnoted.database.dataHelper import DataHelper
from xnoted.errors.databaseError import DatabaseError
from dataclasses import dataclass

PROJECTS_DOCUMENT = "projects"
TASK_DOCUMENT = "tasks"
ACCOUNT_DOCUMENT = "account"
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
    def __init__(self, keyring: DBKeyring) -> None:
        self.keyring = keyring
        self.client: AsyncMongoClient | None = None
        self.database: AsyncDatabase | None = None

    @property
    def is_credentials_set(self) -> bool:
        credentials = self.keyring.get_credentials()

        if not credentials:
            return False
        return bool(credentials.url)

    def _ensure_db(self) -> AsyncDatabase:
        if self.database is None:
            raise DatabaseError(message="Database not initialized", error=None)
        return self.database

    async def initialize(self) -> None:
        try:
            credentials = self.keyring.get_credentials()
            if not credentials:
                raise DatabaseError(message="Missing database credentials", error=None)

            self.client = AsyncMongoClient(credentials.url)
            self.database = self.client[credentials.db_name]
        except ServerSelectionTimeoutError as e:
            raise DatabaseError(message="Failed to connect to database", error=e) from e

    async def _handle_find_all(
        self, document_name: str, helper: Callable[[Dict[str, Any]], T]
    ) -> list[T]:
        db = self._ensure_db()

        try:
            cursor = db[document_name].find()
            results: list[T] = []

            async for doc in cursor:
                results.append(helper(doc))

            return results
        except PyMongoError as e:
            raise DatabaseError(
                message=f"Failed to fetch {document_name}", error=e
            ) from e

    async def _get_projects(self) -> list[Project]:
        return await self._handle_find_all(
            PROJECTS_DOCUMENT,
            lambda d: dataHelper.dict_to_sync_project(d, project_id_key="project_id"),
        )

    async def _get_tasks(self) -> list[Task]:
        return await self._handle_find_all(
            TASK_DOCUMENT,
            lambda d: dataHelper.dict_to_sync_task(d, task_id_key="task_id"),
        )

    async def _get_accounts(self) -> list[Account]:
        return await self._handle_find_all(
            ACCOUNT_DOCUMENT,
            lambda d: dataHelper.dict_to_sync_account(d, account_id_key="account_id"),
        )

    async def _handle_insert(self, *, document_name: str, data: list[T]) -> None:
        db = self._ensure_db()

        try:
            collection = db[document_name]
            payload = []

            for item in data:
                d = cast(Any, item).to_dict()
                d["sync_status"] = SyncStatus.SYNCED.value
                payload.append(d)

            if payload:
                await collection.insert_many(payload)
        except PyMongoError as e:
            raise DatabaseError(
                message=f"Failed to insert into {document_name}", error=e
            ) from e

    async def _handle_delete_tasks(self, data: list[Task]) -> None:
        db = self._ensure_db()

        try:
            ids = [t.task_id for t in data]
            await db[TASK_DOCUMENT].delete_many({"task_id": {"$in": ids}})
        except PyMongoError as e:
            raise DatabaseError(message="Failed to delete tasks", error=e) from e

    async def _handle_delete_projects(self, data: list[Project]) -> None:
        db = self._ensure_db()

        try:
            ids = [p.project_id for p in data]
            await db[PROJECTS_DOCUMENT].delete_many({"project_id": {"$in": ids}})
        except PyMongoError as e:
            raise DatabaseError(message="Failed to delete projects", error=e) from e

    async def _handle_update(
        self, *, document_name: str, filter: dict, data: T
    ) -> None:
        db = self._ensure_db()

        try:
            collection = db[document_name]

            payload = cast(Any, data).to_dict()
            payload["sync_status"] = SyncStatus.SYNCED.value

            await collection.find_one_and_update(filter, {"$set": payload})
        except PyMongoError as e:
            raise DatabaseError(
                message=f"Failed to update {document_name}", error=e
            ) from e

    async def _handle_filter_data(
        self,
        local_data: list[T],
        get_remote_data_handler: Callable[[], Awaitable[list[T]]],
        get_id: Callable[[T], str],
        get_sync_status: Callable[[T], str],
    ) -> DataFilter[T]:
        remote_data = await get_remote_data_handler()

        if not remote_data:
            return DataFilter(added=local_data, removed=[], pending_edit=[])

        remote_by_id = {get_id(p): p for p in remote_data}
        local_by_id = {get_id(p): p for p in local_data}

        added, removed, pending_edit = [], [], []

        for d in local_data:
            if get_sync_status(d) == SyncStatus.PENDING_EDIT.value:
                pending_edit.append(d)

        for d_id, d in remote_by_id.items():
            if (
                d_id not in local_by_id
                and get_sync_status(d) == SyncStatus.SYNCED.value
            ):
                removed.append(d)

        for d_id, d in local_by_id.items():
            if (
                d_id not in remote_by_id
                and get_sync_status(d) == SyncStatus.PENDING.value
            ):
                added.append(d)

        return DataFilter(added=added, removed=removed, pending_edit=pending_edit)

    async def push(self, projects: list[Project]) -> None:
        filtered = await self._handle_filter_data(
            projects,
            self._get_projects,
            lambda d: d.project_id,
            lambda d: d.sync_status or "",
        )

        if filtered.removed:
            await self._handle_delete_projects(filtered.removed)
        if filtered.added:
            await self._handle_insert(
                document_name=PROJECTS_DOCUMENT, data=filtered.added
            )
        if filtered.pending_edit:
            for p in filtered.pending_edit:
                await self._handle_update(
                    document_name=PROJECTS_DOCUMENT,
                    filter={"project_id": p.project_id},
                    data=p,
                )

    async def push_tasks(self, tasks: list[Task]) -> None:
        filtered = await self._handle_filter_data(
            tasks,
            self._get_tasks,
            lambda d: d.task_id,
            lambda d: d.sync_status or "",
        )

        if filtered.removed:
            await self._handle_delete_tasks(filtered.removed)
        if filtered.added:
            await self._handle_insert(document_name=TASK_DOCUMENT, data=filtered.added)
        if filtered.pending_edit:
            for t in filtered.pending_edit:
                await self._handle_update(
                    document_name=TASK_DOCUMENT,
                    filter={"task_id": t.task_id},
                    data=t,
                )

    async def push_accounts(self, accounts: list[Account]) -> None:
        filtered = await self._handle_filter_data(
            accounts,
            self._get_accounts,
            lambda d: d.account_id,
            lambda d: d.sync_status or "",
        )

        if filtered.added:
            await self._handle_insert(
                document_name=ACCOUNT_DOCUMENT, data=filtered.added
            )
        if filtered.pending_edit:
            for a in filtered.pending_edit:
                await self._handle_update(
                    document_name=ACCOUNT_DOCUMENT,
                    filter={"account_id": a.account_id},
                    data=a,
                )

    async def pull(self) -> PullResult:
        try:
            return PullResult(
                projects=await self._get_projects(),
                tasks=await self._get_tasks(),
                accounts=await self._get_accounts(),
            )
        except Exception as e:
            raise DatabaseError(message="Failed to pull data", error=e) from e

    async def close(self) -> None:
        if self.client:
            await self.client.close()
