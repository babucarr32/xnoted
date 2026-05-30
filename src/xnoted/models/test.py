from xnoted.models.project import ProjectExport

external_data = {
    "version": "1.0",
    "exported_at": "2026-05-03T11:45:54.541879",
    "project": {
        "id": "267ffb0d-e378-42f6-b34a-dd8693a993a5",
        "title": "Issues to fix",
        "description": "Issues related to xnoted",
        "type": "task",
        "createdAt": "2026-04-25 22:38:40",
        "sync_status": "synced"
    },
    "tasks": [
        {
            "id": "1351a5b2-614d-465d-a2bf-476811690f15",
            "project_id": "267ffb0d-e378-42f6-b34a-dd8693a993a5",
            "title": "Close forms on create",
            "content": "",
            "is_protected": 1,
            "status": 3,
            "createdAt": "",  # FIX: empty string → None
            "sync_status": "synced"
        }
    ],
    "task_count": 7
}

data = ProjectExport(**external_data)

print(data.project.title)
print(data.model_dump())
