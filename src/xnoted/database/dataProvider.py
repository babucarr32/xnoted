from typing import List, Optional, Protocol
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Task:
    id: str
    project_id: str
    title: str
    content: str
    is_protected: int
    status: int
    createdAt: Optional[str] = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Project:
    id: str
    title: str
    description: str
    type: str
    createdAt: str | None = ""
    sync_status: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class DataHandler(Protocol):
    @property
    def project_name(self) -> str: ...

    @property
    def project_type(self) -> str: ...

    @property
    def is_data_unprotected(self) -> bool: ...

    @is_data_unprotected.setter
    def is_data_unprotected(self, value: bool) -> None: ...

    @property
    def current_project_id(self) -> str | None: ...

    def set_current_project(self, project_id: str) -> None: ...

    def save_task(self, data: Task) -> None: ...

    def save_password(self, password: str) -> None: ...

    def verify_password(self, input_password: str) -> bool: ...

    def has_password(self) -> bool: ...

    def save_project(self, data: Project) -> None: ...

    def update_task(self, task_id: str, data: Task) -> None: ...

    def update_project(self, project_id: str, data: Project) -> None: ...

    def delete_project(self, project_id: str) -> None: ...

    def delete_task(self, task_id: str) -> None: ...

    def get_tasks(self, project_id: str) -> List[Task]: ...

    def get_task(self, task_id: str) -> Task | None: ...

    def load_projects(self) -> List[Project]: ...

    def get_first_project(self) -> Project | None: ...

    def get_project(self, project_id: str) -> Project | None: ...

    def add_task(self, data: Task) -> None: ...

    def update_tasks(self, data: List[Task]) -> None: ...

    def is_storage_exist(self) -> bool: ...

    def is_empty(self) -> bool: ...

    def get_last_id(self, project_id: str) -> str: ...


class DataProvider:
    def __init__(self, provider: DataHandler):
        self.provider = provider

    @property
    def project_name(self) -> str:
        return self.provider.project_name

    @property
    def project_type(self) -> str:
        return self.provider.project_type

    @property
    def is_data_unprotected(self) -> bool:
        return self.provider.is_data_unprotected

    @is_data_unprotected.setter
    def is_data_unprotected(self, value: bool) -> None:
        self.provider.is_data_unprotected = value

    @property
    def current_project_id(self) -> str | None:
        return self.provider.current_project_id

    def set_current_project(self, project_id: str) -> None:
        self.provider.set_current_project(project_id)

    def save_task(self, data: Task) -> None:
        self.provider.save_task(data)

    def save_password(self, password: str) -> None:
        self.provider.save_password(password)

    def verify_password(self, input_password: str) -> bool:
        return self.provider.verify_password(input_password)

    def has_password(self) -> bool:
        """Return True if a password has been set."""
        return self.provider.has_password()

    def save_project(self, data: Project) -> None:
        """Create a new project"""
        self.provider.save_project(data)

    def update_task(self, task_id: str, data: Task):
        """Update an existing task"""
        self.provider.update_task(task_id, data)

    def update_project(self, project_id: str, data: Project) -> None:
        """Update an existing project"""
        self.provider.update_project(project_id, data)

    def delete_project(self, project_id: str) -> None:
        """Delete a project and all its tasks"""
        self.provider.delete_project(project_id)

    def delete_task(self, task_id: str) -> None:
        """Delete a task"""
        self.provider.delete_task(task_id)

    def load_tasks(self, project_id: str) -> List[Task]:
        """Load all tasks for a specific project"""
        return self.provider.get_tasks(project_id)

    def get_task(self, task_id: str) -> Task | None:
        return self.provider.get_task(task_id)

    def load_projects(self) -> List[Project]:
        """Load all projects"""
        return self.provider.load_projects()

    def get_first_project(self) -> Project | None:
        """Get the first project"""
        return self.provider.get_first_project()

    def get_project(self, project_id: str) -> Project | None:
        """Get a specific project by ID"""
        return self.provider.get_project(project_id)

    def add_task(self, data: Task) -> None:
        """Alias for save()"""
        self.provider.add_task(data)

    def update_tasks(self, data: List[Task]) -> None:
        """Batch update/insert tasks for the current project"""
        self.provider.update_tasks(data)

    def is_storage_exist(self) -> bool:
        """Check if storage is accessible"""
        return self.provider.is_storage_exist()

    def is_empty(self) -> bool:
        """Check if the database is empty (exactly 1 project and no tasks).

        Returns:
            True if there's exactly 1 project and 0 tasks, False otherwise
        """
        return self.provider.is_empty()

    def get_last_id(self, project_id: str) -> str:
        """Get the last task ID for a project"""
        return self.provider.get_last_id(project_id)
