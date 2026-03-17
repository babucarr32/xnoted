from typing import Protocol, Optional
from enum import Enum
from dataclasses import dataclass, asdict


class SyncStatus(Enum):
    PENDING = "pending"
    SYNCED = "synced"


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
class Project:
    project_id: str
    title: str
    description: str
    type: str
    createdAt: str | None = ""
    sync_status: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class Sync(Protocol):
    async def initialize(self) -> None: ...

    async def pull(self) -> None: ...

    async def push(self, projects: list[Project]) -> None: ...

    async def push_tasks(self, tasks: list[Task]) -> None: ...


class SyncProvider:
    def __init__(self, sync: Sync):
        self.sync = sync

    async def initialize(self):
        await self.sync.initialize()

    async def pull(self):
        await self.sync.pull()

    async def push(self, projects: list[Project]):
        await self.sync.push(projects)

    async def push_tasks(self, tasks: list[Task]):
        await self.sync.push_tasks(tasks)
