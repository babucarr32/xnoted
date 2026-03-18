import bcrypt
import sqlite3
from typing import List, Optional, cast, Callable, TypeVar, Generic
from xnoted.utils.logger import get_logger
from xnoted.utils.dataDir import DB_NAME
from xnoted.database.dataProvider import Project, Task
from xnoted.sync.syncProvider import SyncStatus
from xnoted.database.dataHelper import DataHelper
from dataclasses import dataclass
from xnoted.queries.sqlQueries import (
    CREATE_TASK_TABLE,
    CREATE_ACCOUNT_TABLE,
    INSERT_TASK_DATA,
    INSERT_ACCOUNT_DATA,
    GET_PASSWORD,
    UPDATE_TASK_DATA,
    UPDATE_PROJECT_SYNC_COLUMN,
    UPDATE_TASK_SYNC_COLUMN,
    QUERY_TASKS_BY_PROJECT,
    QUERY_ONE_TASKS_BY_ID,
    CREATE_PROJECT_TABLE,
    INSERT_PROJECT_DATA,
    UPDATE_PROJECT_DATA,
    QUERY_ALL_PROJECT_DATA,
    UPDATE_TASK_COLUMN,
    QUERY_ONE_PROJECT_DATA,
    DELETE_PROJECT_DATA,
    DELETE_PROJECT_TASKS,
    DELETE_TASK,
)

T = TypeVar("T")
logger = get_logger(__name__)
data_helper = DataHelper()


@dataclass(frozen=True)
class DataFilter(Generic[T]):
    added: list[T]
    removed: list[T]


class SqlDataHandler:
    def __init__(self) -> None:
        self.path = DB_NAME
        self.current_project_id: Optional[str] = None
        self.project_name: str = "Project"
        self.project_type: str = ""
        self.con = sqlite3.connect(DB_NAME)
        self.cur = self.con.cursor()
        self.cur.execute(CREATE_TASK_TABLE)
        self.cur.execute(CREATE_ACCOUNT_TABLE)
        self.cur.execute(CREATE_PROJECT_TABLE)
        self.con.commit()
        self.is_data_unprotected = False

        # Update database with missing column
        if not self._column_exists("task", "is_protected"):
            self.cur.execute(UPDATE_TASK_COLUMN)
            self.con.commit()

        if not self._column_exists("task", "sync_status"):
            self.cur.execute(UPDATE_TASK_SYNC_COLUMN)
            self.con.commit()

        if not self._column_exists("project", "sync_status"):
            self.cur.execute(UPDATE_PROJECT_SYNC_COLUMN)
            self.con.commit()

        # Ensure a default project exists
        self._ensure_default_project()
        projects = self.load_projects()

        if projects:
            self.current_project_id = projects[0].id
            self.project_type = projects[0].type

    def _ensure_default_project(self) -> None:
        """Create a default project if no projects exist"""
        try:
            self.cur.execute("SELECT COUNT(*) FROM project")
            count = self.cur.fetchone()[0]

            if count == 0:
                import uuid

                default_project = Project(
                    id=str(uuid.uuid4()),
                    title="Default",
                    description="Default project",
                    type="general",
                    sync_status=SyncStatus.PENDING.value,
                )
                self.cur.execute(
                    INSERT_PROJECT_DATA,
                    (
                        default_project.id,
                        default_project.title,
                        default_project.description,
                        default_project.type,
                        default_project.sync_status,
                    ),
                )
                self.con.commit()
        except Exception as e:
            logger.error(f"Error creating default project: {e}")

    def _column_exists(self, table, column):
        self.cur.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in self.cur.fetchall()]
        return column in columns

    def set_current_project(self, project_id: str) -> None:
        """Set the current project context"""
        self.current_project_id = project_id
        project = self.get_project(project_id)

        if not project:
            logger.error(f"Project with id {project_id} not found")
            return

        self.project_name = project.title
        self.project_type = project.type

    def save_task(self, data: Task) -> None:
        """Save a task to the current project"""
        if not self.current_project_id:
            logger.error("No project selected. Call set_current_project() first.")
            return

        try:
            status = 0
            new_data = Task(
                id=data.id,
                project_id=data.project_id,
                title=data.title,
                content=data.content,
                status=status,
                is_protected=data.is_protected,
                sync_status=data.sync_status,
            )

            self.cur.execute(
                INSERT_TASK_DATA,
                (
                    new_data.id,
                    new_data.project_id,
                    new_data.title,
                    new_data.content,
                    new_data.is_protected,
                    new_data.status,
                    new_data.sync_status,
                ),
            )
            self.con.commit()
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise

    def save_password(self, password: str) -> None:
        """Save password"""
        try:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            self.cur.execute(
                INSERT_ACCOUNT_DATA,
                (hashed.decode("utf-8"),),
            )
            self.con.commit()
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise

    def verify_password(self, input_password: str) -> bool:
        self.cur.execute(GET_PASSWORD)
        row = self.cur.fetchone()

        if not row:
            return False

        stored_hash = row[0].encode("utf-8")

        return bcrypt.checkpw(input_password.encode("utf-8"), stored_hash)

    def has_password(self) -> bool:
        """Return True if a password has been set."""
        try:
            self.cur.execute(GET_PASSWORD)
            return self.cur.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking password existence: {e}")
            raise

    def save_project(self, data: Project) -> None:
        """Create a new project"""
        try:
            self.cur.execute(
                INSERT_PROJECT_DATA,
                (data.id, data.title, data.description, data.type, data.sync_status),
            )
            self.con.commit()
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            raise

    def update_task(self, task_id: str, data: Task) -> None:
        """Update an existing task"""
        try:
            self.cur.execute(
                UPDATE_TASK_DATA,
                (
                    data.title,
                    data.content,
                    data.is_protected,
                    data.status,
                    data.sync_status,
                    task_id,
                ),
            )
            self.con.commit()
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise

    def update_project(self, project_id: str, data: Project) -> None:
        """Update an existing project"""
        try:
            self.cur.execute(
                UPDATE_PROJECT_DATA,
                (data.title, data.description, data.type, data.sync_status, project_id),
            )
            self.con.commit()
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            raise

    def delete_project(self, project_id: str) -> None:
        """Delete a project and all its tasks"""
        try:
            self.cur.execute(DELETE_PROJECT_TASKS, (project_id,))
            self.cur.execute(DELETE_PROJECT_DATA, (project_id,))
            self.con.commit()
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            raise

    def delete_task(self, task_id: str) -> None:
        """Delete a task"""
        try:
            self.cur.execute(DELETE_TASK, (task_id,))
            self.con.commit()
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            raise

    def get_tasks(self, project_id: str) -> List[Task]:
        """Load all tasks for a specific project"""
        try:
            res = self.cur.execute(QUERY_TASKS_BY_PROJECT, (project_id,))
            rows = res.fetchall()
            return [
                Task(
                    id=row[0],
                    title=row[1],
                    project_id=project_id,
                    content=row[2],
                    is_protected=False if self.is_data_unprotected else row[3],
                    status=row[4],
                    sync_status=row[5],
                    createdAt=row[6],
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return []

    def get_task(self, task_id: str) -> Task | None:
        if not task_id:
            logger.error("No task id specified. Provide task_id.")
            return None

        try:
            res = self.cur.execute(QUERY_ONE_TASKS_BY_ID, (task_id,))
            row = res.fetchone()
            return Task(
                id=row[0],
                title=row[1],
                project_id=cast(str, self.current_project_id),
                content=row[2],
                is_protected=False if self.is_data_unprotected else row[3],
                status=row[4],
                sync_status=row[5],
                createdAt=row[6],
            )
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None

    def load_projects(self) -> List[Project]:
        """Load all projects"""
        try:
            res = self.cur.execute(QUERY_ALL_PROJECT_DATA)
            rows = res.fetchall()
            return [data_helper.tuple_to_project(row) for row in rows]
        except Exception as e:
            logger.error(f"Error loading projects: {e}")
            return []

    def get_first_project(self) -> Project | None:
        """Get the first project"""
        try:
            res = self.cur.execute(QUERY_ALL_PROJECT_DATA)
            row = res.fetchone()
            return data_helper.tuple_to_project(row)
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            return None

    def get_project(self, project_id: str) -> Project | None:
        """Get a specific project by ID"""
        try:
            self.cur.execute(QUERY_ONE_PROJECT_DATA, (project_id,))
            row = self.cur.fetchone()
            if row:
                return data_helper.tuple_to_project(row)
            return None
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            return None

    def add_task(self, data: Task) -> None:
        """Add new task"""
        self.save_task(data)

    def is_storage_exist(self) -> bool:
        """Check if storage is accessible"""
        try:
            self.cur.execute("SELECT 1 FROM task LIMIT 1")
            return True
        except Exception:
            return False

    def is_empty(self) -> bool:
        """Check if the database is empty (exactly 1 project and no tasks).

        Returns:
            True if there's exactly 1 project and 0 tasks, False otherwise
        """
        try:
            self.cur.execute("SELECT COUNT(*) FROM project")
            project_count = self.cur.fetchone()[0]

            self.cur.execute("SELECT COUNT(*) FROM task")
            task_count = self.cur.fetchone()[0]

            return project_count == 1 and task_count == 0
        except Exception:
            return True

    def get_last_id(self, project_id: str) -> str:
        """Get the last task ID for a project"""
        tasks = self.get_tasks(project_id)
        if tasks:
            return tasks[-1].id
        return "0"

    def _handle_filter_data(
        self,
        incoming_data: list[T],
        existing_data: list[T],
        get_id: Callable[[T], str],
        get_sync_status: Callable[[T], str],
    ) -> DataFilter[T] | None:
        existing_data
        if not existing_data:
            return DataFilter(added=incoming_data, removed=[])

        existing_by_id = {get_id(p): p for p in existing_data}
        incoming_by_id = {get_id(p): p for p in incoming_data}

        added: list[T] = []
        removed: list[T] = []

        # removed
        for d_id, d in existing_by_id.items():
            if (
                d_id not in incoming_by_id
                and get_sync_status(d) == SyncStatus.SYNCED.value
            ):
                removed.append(d)

        # added
        for d_id, d in incoming_by_id.items():
            if (
                d_id not in existing_by_id
                and get_sync_status(d) == SyncStatus.SYNCED.value
            ):
                added.append(d)

        return DataFilter(added=added, removed=removed)

    def sync(
        self, incoming_tasks: list[Task], incoming_projects: list[Project]
    ) -> None:
        projects = self.load_projects()
        tasks: list[Task] = []

        self.load_projects()

        for p in projects:
            tasks = [*tasks, *self.get_tasks(p.id)]

        filtered_project: DataFilter[Project] | None = self._handle_filter_data(
            incoming_data=incoming_projects,
            existing_data=projects,
            get_id=lambda p: p.id,
            get_sync_status=lambda p: p.sync_status or "",
        )

        filtered_task: DataFilter[Task] | None = self._handle_filter_data(
            incoming_data=incoming_tasks,
            existing_data=tasks,
            get_id=lambda t: t.id,
            get_sync_status=lambda t: t.sync_status or "",
        )

        if filtered_project:
            # Add project
            for project in filtered_project.added:
                self.save_project(project)

            # Delete project
            for project in filtered_project.removed:
                self.delete_project(project.id)

        if filtered_task:
            # Add Task
            for task in filtered_task.added:
                self.add_task(task)

            # Delete task
            for task in filtered_task.removed:
                self.delete_task(task.id)

    def __del__(self) -> None:
        if hasattr(self, "con"):
            self.con.close()
