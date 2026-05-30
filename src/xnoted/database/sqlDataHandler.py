import bcrypt
import sqlite3
from typing import List, Optional, cast, Callable, TypeVar, Generic, TypeAlias, Literal
from xnoted.utils.helpers import derive_encryption_key
from xnoted.utils.dataDir import DB_PATH
from xnoted.errors.projectNotFoundError import ProjectNotFoundError
from xnoted.errors.encryptionError import EncryptionError
from xnoted.errors.passwordError import PasswordError
from xnoted.errors.decryptionError import DecryptionError
from xnoted.errors.accountError import AccountError
from xnoted.errors.currentProjectNotFoundError import CurrentProjectNotFoundError
from xnoted.errors.databaseError import DatabaseError
from xnoted.utils.constants import DEFAULT_ACCOUNT_ID
from xnoted.database.dataProvider import Project, Task, Account, ProtectionStatus
from xnoted.sync.syncProvider import SyncStatus
from cryptography.fernet import Fernet, InvalidToken
from xnoted.database.dataHelper import DataHelper, ProjectRow, TaskRow, AccountRow
from dataclasses import dataclass
from xnoted.queries.sqlQueries import (
    CREATE_TASK_TABLE,
    CREATE_ACCOUNT_TABLE,
    INSERT_TASK_DATA,
    INSERT_ACCOUNT_DATA,
    GET_PASSWORD,
    DELETE_TASK_ON_PROJECT_ID,
    QUERY_ALL_ACCOUNT_DATA,
    QUERY_ONE_ACCOUNT_DATA,
    UPDATE_TASK_DATA,
    UPDATE_ACCOUNT_SYNC_COLUMN,
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
SeverityLevel: TypeAlias = Literal["information", "warning", "error"]
data_helper = DataHelper()


@dataclass(frozen=True)
class DataFilter(Generic[T]):
    added: list[T]
    removed: list[T]


class SqlDataHandler:
    def __init__(self) -> None:
        self.path = DB_PATH
        self.current_project_id: Optional[str] = None
        self.project_name: str = "Project"
        self.project_type: str = ""
        self.con = sqlite3.connect(DB_PATH)
        self.cur = self.con.cursor()
        self.cur.execute(CREATE_TASK_TABLE)
        self.cur.execute(CREATE_ACCOUNT_TABLE)
        self.cur.execute(CREATE_PROJECT_TABLE)
        self.con.commit()
        self.is_data_unprotected = False

        # Update database with missing column
        self.update_missing_column()

        # Ensure a default project exists
        self._ensure_default_project()
        projects = self.load_projects()

        if projects:
            self.current_project_id = projects[0].id
            self.project_type = projects[0].type

    def update_missing_column(self):
        if not self._column_exists("task", "is_protected"):
            self.cur.execute(UPDATE_TASK_COLUMN)
            self.con.commit()

        if not self._column_exists("task", "sync_status"):
            self.cur.execute(UPDATE_TASK_SYNC_COLUMN)
            self.con.commit()

        if not self._column_exists("project", "sync_status"):
            self.cur.execute(UPDATE_PROJECT_SYNC_COLUMN)
            self.con.commit()

        if not self._column_exists("account", "sync_status"):
            self.cur.execute(UPDATE_ACCOUNT_SYNC_COLUMN)
            self.con.commit()

    @property
    def is_password_set(self) -> bool:
        return bool(self._get_password())

    def _ensure_default_project(self) -> None:
        """Create a default project if no projects exist"""
        try:
            self.cur.execute("SELECT COUNT(*) FROM project")
            count = self.cur.fetchone()[0]

            if count > 0:
                return

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
            self.con.rollback()
            raise DatabaseError(
                message="Error creating default project", error=e
            ) from e

    def _column_exists(self, table, column):
        self.cur.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in self.cur.fetchall()]
        return column in columns

    def set_current_project(self, project_id: str) -> None:
        """Set the current project context"""
        self.current_project_id = project_id
        project = self.get_project(project_id)

        if not project:
            raise ProjectNotFoundError(project_id=project_id)

        self.project_name = project.title
        self.project_type = project.type

    def save_task(self, data: Task) -> None:
        """Save a task to the current project"""
        if not self.current_project_id:
            raise CurrentProjectNotFoundError()

        try:
            self.cur.execute(
                INSERT_TASK_DATA,
                (
                    data.id,
                    data.project_id,
                    data.title,
                    data.content,
                    data.is_protected,
                    data.status,
                    data.createdAt,
                    data.sync_status,
                ),
            )
            self.con.commit()
        except Exception as e:
            raise DatabaseError(message="Error saving task", error=e) from e

    def _encrypt_task(self, *, encryption_key: str, task: Task) -> Task | None:
        """Encrypt a task"""

        encrypted_content = self._encrypt_data(
            encryption_key=encryption_key, data=task.content
        )
        encrypted_title = self._encrypt_data(
            encryption_key=encryption_key, data=task.title
        )

        return Task(
            id=task.id,
            project_id=task.project_id,
            title=encrypted_title,
            content=encrypted_content,
            status=task.status,
            is_protected=task.is_protected,
            sync_status=task.sync_status,
        )

    def encrypt_task(self, task_id: str) -> Task:
        """Encrypt a task"""
        task = self.get_task(task_id)
        if not task:
            raise EncryptionError(message=f"Task with id {task_id} not found")

        encrypted_password = self._get_password()
        if not encrypted_password:
            raise EncryptionError(message="Password not found, create password first.")

        decoded_encrypted_password = encrypted_password.decode("utf-8")
        encrypted_content = self._encrypt_data(
            encryption_key=decoded_encrypted_password, data=task.content
        )
        encrypted_title = self._encrypt_data(
            encryption_key=decoded_encrypted_password, data=task.title
        )

        return Task(
            id=task.id,
            project_id=task.project_id,
            title=encrypted_title,
            content=encrypted_content,
            status=task.status,
            is_protected=ProtectionStatus.PROTECTED.value,
            sync_status=task.sync_status,
        )

    def decrypt_task(self, task_id: str) -> Task:
        """Decrypt a task"""
        task = self.get_task(task_id)
        if not task:
            raise DecryptionError(
                message=f"Decryption failed, task with id {task_id} not found"
            )

        encrypted_password = self._get_password()
        if not encrypted_password:
            raise DecryptionError(message="Password not found, create password first.")

        decoded_encrypted_password = encrypted_password.decode("utf-8")
        decrypted_content = self._decrypt_data(
            encryption_key=decoded_encrypted_password, data=task.content
        )
        decrypted_title = self._decrypt_data(
            encryption_key=decoded_encrypted_password, data=task.title
        )

        return Task(
            id=task.id,
            project_id=task.project_id,
            title=decrypted_title,
            content=decrypted_content,
            status=task.status,
            is_protected=ProtectionStatus.NOT_PROTECTED.value,
            sync_status=task.sync_status,
        )

    def _decrypt_task(self, *, encryption_key: str, task: Task) -> Task | None:
        """Decrypt a task"""

        if task.content:
            decrypted_content = self._decrypt_data(
                encryption_key=encryption_key, data=task.content
            )
        decrypted_title = self._decrypt_data(
            encryption_key=encryption_key, data=task.title
        )

        return Task(
            id=task.id,
            project_id=task.project_id,
            title=decrypted_title,
            content=decrypted_content or task.content,
            status=task.status,
            is_protected=task.is_protected,
            sync_status=task.sync_status,
        )

    def _get_protection_status(self, protection_status: int) -> int:
        return (
            ProtectionStatus.NOT_PROTECTED.value
            if self.is_data_unprotected
            else ProtectionStatus.PROTECTED.value
            if protection_status == ProtectionStatus.PROTECTED.value
            else ProtectionStatus.NOT_PROTECTED.value
        )

    def _maybe_decrypt(
        self,
        *,
        should_decrypt: bool,
        encryption_key: str | None,
        value: str,
    ) -> str:
        if not encryption_key:
            return value

        if should_decrypt:
            return self._decrypt_data(
                encryption_key=encryption_key,
                data=value,
            )
        return value

    def _get_encryption_key(self) -> str | None:
        password_bytes = self._get_password()
        encryption_key = password_bytes.decode("utf-8") if password_bytes else None
        return encryption_key

    def _get_cipher(self, encryption_key: str) -> Fernet:
        key = derive_encryption_key(encryption_key)
        return Fernet(key)

    def _encrypt_data(self, *, encryption_key: str, data: str) -> str:
        cipher = self._get_cipher(encryption_key)
        return cipher.encrypt(data.encode("utf-8")).decode("utf-8")

    def _decrypt_data(self, *, encryption_key: str, data: str) -> str:
        cipher = self._get_cipher(encryption_key)

        try:
            return cipher.decrypt(data.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            raise DecryptionError(message="Unable to decrypt data, invalid password.")

    def _update_account_password(self, password: str) -> None:
        account = self.get_account()
        if not account:
            raise AccountError(message="Unable to update password, account not found.")

        self.save_account(
            Account(
                id=account.id,
                password=password,
                sync_status=SyncStatus.PENDING_EDIT.value,
            )
        )

    def _update_encrypted_data(
        self,
        *,
        old_encryption_key: str,
        password: str,
        new_encryption_key: str,
    ) -> None:
        projects = self.load_projects()
        if not projects:
            return

        for project in projects:
            tasks = self.get_tasks(project.id)
            if not tasks:
                continue

            for task in tasks:
                if not task.is_protected:
                    continue

                decrypted = self._decrypt_task(
                    encryption_key=old_encryption_key,
                    task=task,
                )
                if not decrypted:
                    continue

                encrypted = self._encrypt_task(
                    encryption_key=new_encryption_key,
                    task=decrypted,
                )

                if not encrypted:
                    continue

                self.update_task(
                    encrypted.id,
                    Task(
                        id=encrypted.id,
                        project_id=encrypted.project_id,
                        title=encrypted.title,
                        content=encrypted.content,
                        is_protected=encrypted.is_protected,
                        status=encrypted.status,
                        sync_status=SyncStatus.PENDING_EDIT.value,
                        createdAt=encrypted.createdAt,
                    ),
                )

        self._update_account_password(password)

    def save_account(self, data: Account) -> None:
        """Save account"""
        try:
            self.cur.execute(
                INSERT_ACCOUNT_DATA,
                (data.password, data.sync_status),
            )
            self.con.commit()

        except Exception as e:
            raise DatabaseError(message="Error saving account.", error=e)

    def _hash_password(self, password: str) -> str:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def edit_password(self, password: str) -> None:
        """Save password"""
        hashed_password = self._hash_password(password)
        old_encryption_key = self._get_encryption_key()

        if not old_encryption_key:
            raise EncryptionError("Encryption key not found.")

        self._update_encrypted_data(
            old_encryption_key=old_encryption_key,
            password=hashed_password,
            new_encryption_key=hashed_password,
        )

        account = self.get_account()
        account_id = DEFAULT_ACCOUNT_ID

        if not account:
            raise AccountError(message="Account not found.")

        account_id = account.id
        account_data = Account(
            id=account_id,
            password=hashed_password,
            sync_status=SyncStatus.PENDING_EDIT.value,
        )
        self.save_account(account_data)

    def save_password(self, password: str) -> None:
        """Save password"""
        hashed_password = self._hash_password(password)
        account_id = DEFAULT_ACCOUNT_ID
        sync_status = SyncStatus.PENDING.value
        account_data = Account(
            id=account_id, password=hashed_password, sync_status=sync_status
        )
        self.save_account(account_data)

    def _get_password(self) -> bytes | None:
        self.cur.execute(GET_PASSWORD)
        row = self.cur.fetchone()
        return None if not row else row[0].encode("utf-8")

    def verify_password(self, input_password: str) -> bool:
        stored_hash = self._get_password()

        if not stored_hash:
            raise PasswordError(message="Verification failed, password not found.")

        return bcrypt.checkpw(input_password.encode("utf-8"), stored_hash)

    @property
    def has_password(self) -> bool:
        """Return True if a password has been set."""
        try:
            self.cur.execute(GET_PASSWORD)
            return self.cur.fetchone() is not None
        except Exception as e:
            raise PasswordError(message="Unable to get password.", error=e)

    def save_project(self, data: Project) -> None:
        """Create a new project"""
        try:
            self.cur.execute(
                INSERT_PROJECT_DATA,
                (data.id, data.title, data.description, data.type, data.sync_status),
            )
            self.con.commit()
        except Exception as e:
            raise DatabaseError(message="Error saving project", error=e)

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
            raise DatabaseError(message="Error updating task.", error=e)

    def update_project(self, project_id: str, data: Project) -> None:
        """Update an existing project"""
        try:
            self.cur.execute(
                UPDATE_PROJECT_DATA,
                (data.title, data.description, data.type, data.sync_status, project_id),
            )
            self.con.commit()
        except Exception as e:
            raise DatabaseError(
                message=f"Error updating project with id {project_id}.", error=e
            )

    def delete_project(self, project_id: str) -> None:
        """Delete a project and all its tasks"""
        try:
            self.cur.execute(DELETE_PROJECT_TASKS, (project_id,))
            self.cur.execute(DELETE_PROJECT_DATA, (project_id,))
            self.con.commit()
            self._delete_tasks_by_project_id(project_id)
        except Exception as e:
            raise DatabaseError(
                message=f"Error deleting project with id {project_id}.", error=e
            )

    def delete_task(self, task_id: str) -> None:
        """Delete a task"""
        try:
            self.cur.execute(DELETE_TASK, (task_id,))
            self.con.commit()
        except Exception as e:
            raise DatabaseError(
                message=f"Error deleting task with id {task_id}.", error=e
            )

    def _delete_tasks_by_project_id(self, project_id: str) -> None:
        """Delete tasks by project id"""
        try:
            self.cur.execute(DELETE_TASK_ON_PROJECT_ID, (project_id,))
            self.con.commit()
        except Exception as e:
            raise DatabaseError(
                message=f"Error deleting tasks with id {project_id}", error=e
            )

    def get_tasks(self, project_id: str) -> List[Task]:
        """Load all tasks for a specific project"""
        encryption_key = self._get_encryption_key()

        try:
            rows = self.cur.execute(QUERY_TASKS_BY_PROJECT, (project_id,)).fetchall()
            encryption_key = self._get_encryption_key()

            tasks: List[Task] = []

            for row in rows:
                tasks.append(
                    Task(
                        id=row[0],
                        project_id=row[1],
                        title=self._maybe_decrypt(
                            should_decrypt=self.is_data_unprotected and row[4],
                            encryption_key=encryption_key,
                            value=row[2],
                        ),
                        content=self._maybe_decrypt(
                            should_decrypt=self.is_data_unprotected and row[4],
                            encryption_key=encryption_key,
                            value=row[3],
                        ),
                        is_protected=self._get_protection_status(row[4]),
                        status=row[5],
                        sync_status=row[6],
                        createdAt=row[7],
                    )
                )

            return tasks

        except Exception as e:
            raise DatabaseError(message="Error getting tasks", error=e)

    def get_accounts(self) -> List[Account]:
        """Load all tasks for a specific project"""
        try:
            accounts = self.cur.execute(QUERY_ALL_ACCOUNT_DATA).fetchall()
        except Exception as e:
            raise DatabaseError(message="Error getting accounts", error=e)
        return [data_helper.tuple_to_account(account) for account in accounts]

    def get_account(self) -> Account | None:
        try:
            account: AccountRow = self.cur.execute(QUERY_ONE_ACCOUNT_DATA).fetchone()
            if not account:
                return None
        except Exception as e:
            raise DatabaseError(message="Unable to get account.", error=e)

        return data_helper.tuple_to_account(account)

    def get_task(self, task_id: str) -> Task | None:
        try:
            task: TaskRow = self.cur.execute(
                QUERY_ONE_TASKS_BY_ID, (task_id,)
            ).fetchone()
            if not task:
                return None
        except Exception as e:
            raise DatabaseError(
                message=f"Error getting task with id {task_id}", error=e
            )

        encryption_key = self._get_encryption_key()
        return Task(
            id=task[0],
            project_id=cast(str, task[1]),
            title=self._maybe_decrypt(
                should_decrypt=self.is_data_unprotected and task[4],
                encryption_key=encryption_key,
                value=task[2],
            ),
            content=self._maybe_decrypt(
                should_decrypt=self.is_data_unprotected and task[4],
                encryption_key=encryption_key,
                value=task[3],
            ),
            is_protected=self._get_protection_status(task[4]),
            status=task[5],
            sync_status=task[6],
            createdAt=task[7],
        )

    def load_projects(self) -> List[Project]:
        """Load all projects"""
        try:
            rows: list[ProjectRow] = self.cur.execute(QUERY_ALL_PROJECT_DATA).fetchall()
        except Exception as e:
            raise DatabaseError(message="Error loading projects", error=e)
        return [data_helper.tuple_to_project(row) for row in rows]

    def get_first_project(self) -> Project | None:
        """Get the first project"""
        try:
            project = self.cur.execute(QUERY_ALL_PROJECT_DATA).fetchone()
            if not project:
                return None
        except Exception as e:
            raise DatabaseError(message="Error getting first project", error=e)
        return data_helper.tuple_to_project(project)

    def get_project(self, project_id: str) -> Project | None:
        """Get a specific project by ID"""
        try:
            row = self.cur.execute(QUERY_ONE_PROJECT_DATA, (project_id,)).fetchone()
            if not row:
                return None
        except Exception as e:
            raise DatabaseError(
                message=f"Error getting project with id {project_id}", error=e
            )

        return data_helper.tuple_to_project(row)

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
        self,
        *,
        incoming_tasks: list[Task],
        incoming_projects: list[Project],
        incoming_accounts: list[Account],
    ) -> None:
        projects = self.load_projects()
        tasks: list[Task] = []

        if projects:
            if accounts := self.get_accounts():
                for p in projects:
                    if res := self.get_tasks(p.id):
                        tasks.extend(res)

                filtered_account: DataFilter[Account] | None = self._handle_filter_data(
                    incoming_data=incoming_accounts,
                    existing_data=accounts,
                    get_id=lambda p: p.id,
                    get_sync_status=lambda p: p.sync_status or "",
                )

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

        if filtered_account:
            # Add account
            for account in filtered_account.added:
                self.save_account(account)

            # Delete account
            # Will be implemented later

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
