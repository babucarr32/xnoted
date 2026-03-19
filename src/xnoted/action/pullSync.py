from xnoted.sync.syncProvider import SyncProvider
from xnoted.database.dataProvider import DataProvider, Task, Project

async def pull_sync(sync: SyncProvider, data_provider: DataProvider) -> None:
    await sync.initialize()
    pull_result = await sync.pull()

    incoming_tasks = [
        Task(
            id=t.task_id,
            title=t.title,
            content=t.content,
            project_id=t.project_id,
            status=t.status,
            is_protected=t.is_protected,
            createdAt=t.createdAt,
            sync_status=t.sync_status,
        )
        for t in pull_result.tasks
    ]

    incoming_projects = [
        Project(
            id=p.project_id,
            title=p.title,
            description=p.description,
            type=p.type,
            createdAt=p.createdAt,
            sync_status=p.sync_status,
        )
        for p in pull_result.projects
    ]

    data_provider.sync(
        incoming_tasks,
        incoming_projects,
    )

