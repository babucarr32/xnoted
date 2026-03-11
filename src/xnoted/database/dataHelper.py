from typing import Any, Dict, TypeAlias
from xnoted.database.dataProvider import Project, Task

TaskRow: TypeAlias = tuple[str, str, str, str, int, int, str]
ProjectRow: TypeAlias = tuple[str, str, str, str, str, str]


class DataHelper:
    def _dict_to_task(self, data: Dict[str, Any]) -> Task:
        return Task(
            id=data["id"],
            project_id=data["project_id"],
            title=data["title"],
            content=data["content"],
            is_protected=data["is_protected"],
            status=data["status"],
            createdAt=data["createdAt"],
        )

    def _dict_to_project(self, data: Dict[str, Any]) -> Project:
        return Project(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            type=data["type"],
            createdAt=data["createdAt"],
        )

    def _tuple_to_task(self, data: TaskRow) -> Task:
        return Task(
            id=data[0],
            project_id=data[1],
            title=data[2],
            content=data[3],
            is_protected=data[4],
            status=data[5],
            createdAt=data[6],
        )

    def _tuple_to_project(self, data: ProjectRow) -> Project:
        return Project(
            id=data[0],
            title=data[1],
            description=data[2],
            type=data[3],
            createdAt=data[4],
        )
