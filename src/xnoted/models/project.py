from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel

SYNC_STATUSES = Literal["pending", "synced", "pending-edit"]
PROTECTION = Literal[0, 1]
TASK_STATUS = Literal[0, 1, 2, 3, 4]


class ProjectData(BaseModel):
    id: str
    title: str
    description: str
    type: str
    createdAt: datetime
    sync_status: SYNC_STATUSES


class Task(BaseModel):
    id: str
    project_id: str
    title: str
    content: str
    is_protected: PROTECTION
    status: TASK_STATUS
    createdAt: datetime
    sync_status: SYNC_STATUSES


class ProjectExport(BaseModel):
    version: str
    exported_at: datetime
    project: ProjectData
    tasks: List[Task]
    task_count: int
