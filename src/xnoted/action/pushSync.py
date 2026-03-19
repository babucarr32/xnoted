from xnoted.sync.syncProvider import SyncStatus
from xnoted.sync.syncProvider import Project as SyncProject
from xnoted.sync.syncProvider import Task as SyncTask
from xnoted.sync.syncProvider import SyncProvider
from xnoted.database.dataProvider import DataProvider, Task, Project

async def push_sync(sync: SyncProvider, data_provider: DataProvider) -> None:
    await sync.initialize()
    projects = data_provider.load_projects()

    # Push projects
    await sync.push(
        [
            SyncProject(
                title=p.title,
                description=p.description,
                type=p.type,
                createdAt=p.createdAt,
                sync_status=p.sync_status,
                project_id=p.id,
            )
            for p in projects
        ]
    )

    # Update status on sync success
    for project in projects:
        if project.sync_status == SyncStatus.PENDING.value:
            data_provider.update_project(
                project.id,
                Project(
                    id=project.id,
                    title=project.title,
                    description=project.description,
                    type=project.type,
                    createdAt=project.createdAt,
                    sync_status=SyncStatus.SYNCED.value,
                ),
            )

    # Push tasks
    tasks: list[Task] = []
    for p in projects:
        tasks = [*tasks, *data_provider.load_tasks(p.id)]

    await sync.push_tasks(
        [
            SyncTask(
                task_id=p.id,
                project_id=p.project_id,
                title=p.title,
                content=p.content,
                is_protected=p.is_protected,
                status=p.status,
                createdAt=p.createdAt,
                sync_status=p.sync_status,
            )
            for p in tasks
        ]
    )

    # Update status on sync success
    for task in tasks:
        if task.sync_status == SyncStatus.PENDING.value:
            data_provider.update_task(
                task.id,
                Task(
                    id=task.id,
                    project_id=task.project_id,
                    title=task.title,
                    content=task.content,
                    is_protected=task.is_protected,
                    status=task.status,
                    createdAt=task.createdAt,
                    sync_status=SyncStatus.SYNCED.value,
                ),
            )

