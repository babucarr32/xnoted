from typing import Any, Dict, TypeAlias
from xnoted.database.dataProvider import Project, Task
from xnoted.sync.syncProvider import Project as SyncProject
from xnoted.sync.syncProvider import Task as SyncTask

TaskRow: TypeAlias = tuple[str, str, str, str, int, int, str, str]
ProjectRow: TypeAlias = tuple[str, str, str, str, str, str, str]


class DataHelper:
    def dict_to_task(self, data: Dict[str, Any]) -> Task:
        return Task(
            id=data["id"],
            project_id=data["project_id"],
            title=data["title"],
            content=data["content"],
            is_protected=data["is_protected"],
            status=data["status"],
            sync_status=data["sync_status"],
            createdAt=data["createdAt"],
        )

    def dict_to_sync_task(self, data: Dict[str, Any], task_id_key = 'id') -> SyncTask:
        return SyncTask(
            task_id=data[task_id_key],
            project_id=data["project_id"],
            title=data["title"],
            content=data["content"],
            is_protected=data["is_protected"],
            status=data["status"],
            sync_status=data["sync_status"],
            createdAt=data["createdAt"],
        )

    def dict_to_project(self, data: Dict[str, Any]) -> Project:
        return Project(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            type=data["type"],
            sync_status=data["sync_status"],
            createdAt=data["createdAt"],
        )

    def dict_to_sync_project(self, data: Dict[str, Any], project_id_key = 'id') -> SyncProject:
        return SyncProject(
            project_id=data[project_id_key],
            title=data["title"],
            description=data["description"],
            type=data["type"],
            sync_status=data["sync_status"],
            createdAt=data["createdAt"],
        )

    def tuple_to_task(self, data: TaskRow) -> Task:
        return Task(
            id=data[0],
            project_id=data[1],
            title=data[2],
            content=data[3],
            is_protected=data[4],
            status=data[5],
            sync_status=data[6],
            createdAt=data[7],
        )

    def tuple_to_project(self, data: ProjectRow) -> Project:
        return Project(
            id=data[0],
            title=data[1],
            description=data[2],
            type=data[3],
            sync_status=data[4],
            createdAt=data[5],
        )
