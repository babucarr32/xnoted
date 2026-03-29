from typing import Protocol, Optional
from enum import Enum
from dataclasses import dataclass, asdict


class SyncStatus(Enum):
    PENDING = "pending"
    SYNCED = "synced"
    PENDING_EDIT = "pending-edit"


@dataclass(frozen=True)
class Task:
    project_id: str
    task_id: str
    title: str
    content: str
    is_protected: int
    status: int
    createdAt: Optional[str] = ""
    sync_status: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

@dataclass(frozen=True)
class Account:
    account_id: str
    password: str
    createdAt: Optional[str] = ""
    sync_status: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Project:
    project_id: str
    title: str
    description: str
    type: str
    createdAt: str | None = ""
    sync_status: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PullResult:
    projects: list[Project]
    tasks: list[Task]
    accounts: list[Account]


class Sync(Protocol):
    @property
    def is_credentials_set(self) -> bool: ...

    async def initialize(self) -> None: ...

    async def pull(self) -> PullResult: ...

    async def push(self, projects: list[Project]) -> None: ...

    async def push_accounts(self, accounts: list[Account]) -> None: ...

    async def push_tasks(self, tasks: list[Task]) -> None: ...


class SyncProvider:
    def __init__(self, sync: Sync):
        self.sync = sync

    def _require_credentials(self):
        if not self.sync.is_credentials_set:
            raise ValueError("DB Credentials not provided")

    async def initialize(self) -> None:
        self._require_credentials()
        await self.sync.initialize()

    async def pull(self) -> PullResult:
        self._require_credentials()
        return await self.sync.pull()

    async def push(self, projects: list[Project]) -> None:
        self._require_credentials()
        await self.sync.push(projects)

    async def push_accounts(self, accounts: list[Account]) -> None:
        self._require_credentials()
        await self.sync.push_accounts(accounts)

    async def push_tasks(self, tasks: list[Task]) -> None:
        self._require_credentials()
        await self.sync.push_tasks(tasks)
