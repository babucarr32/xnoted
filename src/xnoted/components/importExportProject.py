import json
from typing import Iterator, Callable, Any
from pathlib import Path
from datetime import datetime
from textual.containers import Container
from textual.widgets import RadioSet, RadioButton, Input
from textual.app import ComposeResult
from xnoted.errors.errorHandler import ErrorHandler
from xnoted.database.dataHelper import DataHelper
import uuid
from pydantic import ValidationError
from xnoted.models.project import ProjectExport
from xnoted.database.dataProvider import DataProvider, Task, Project
from xnoted.utils.constants import (
    EXPORT_PROJECT_ID,
    IMPORT_PROJECT_ID,
    EXPORT_PROJECT_RADIO_ID,
)
from xnoted.config.manager import ConfigHandler


data_helper = DataHelper()


class ProjectTypeContainer(RadioSet):
    def __init__(self) -> None:
        super().__init__(id=EXPORT_PROJECT_RADIO_ID)
        self.border_title = "Import or Export project"

    def compose(self) -> Iterator[RadioButton]:
        yield RadioButton("Import", id=IMPORT_PROJECT_ID, value=True)
        yield RadioButton("Export", id=EXPORT_PROJECT_ID)


class ImportExportProject(Container):
    def __init__(
        self,
        config_handler: ConfigHandler,
        data_provider: DataProvider,
        on_submit=Callable[[], Any],
    ):
        super().__init__()
        self.data_provider = data_provider
        self.on_submit = on_submit
        self.config_handler = config_handler

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.form

        self._bindings.bind(
            keys=kb.save,
            action="import_export",
            description="Export or Import",
            priority=True,
        )

    def compose(self) -> ComposeResult:
        yield ProjectTypeContainer()
        yield Input(placeholder="File path (e.g., export.json)", id="file_path_input")

    def action_import_export(
        self,
    ) -> None:
        """Handle execute button press"""
        try:
            radio_set = self.query_one(ProjectTypeContainer)
            selected = radio_set.pressed_button

            if selected and selected.id == EXPORT_PROJECT_ID:
                self.handle_export()
            elif selected and selected.id == IMPORT_PROJECT_ID:
                self.handle_import()
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def handle_export(self) -> None:
        """Export current project and its tasks to JSON"""
        try:
            file_path_input = self.query_one("#file_path_input", Input)
            file_path = file_path_input.value.strip()

            if not file_path:
                file_path = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            if not file_path.endswith(".json"):
                file_path += ".json"

            # Get current project
            if not self.data_provider.current_project_id:
                self._update_status("No project selected", "error")
                return

            project = self.data_provider.get_project(
                self.data_provider.current_project_id
            )

            if not project:
                self._update_status("Project not found", "error")
                return

            # Get all tasks for the project
            if tasks := self.data_provider.get_tasks(
                self.data_provider.current_project_id
            ):
                # Create export data structure
                export_data = {
                    "version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "project": project.to_dict(),
                    "tasks": [task.to_dict() for task in tasks],
                    "task_count": len(tasks),
                }

                # Write to file
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                self._update_status(f"Successfully exported to {file_path}", "success")

            self.on_submit()
        except Exception as e:
            self._update_status("Failed to export", "error")
            raise Exception("Something we wrong, failed to export") from e

    def handle_import(self) -> None:
        """Import project and tasks from JSON"""
        try:
            file_path_input = self.query_one("#file_path_input", Input)
            file_path = file_path_input.value.strip()

            if not file_path:
                self._update_status("Please enter a file path", "error")
                return

            if not Path(file_path).exists():
                self._update_status(f"File not found: {file_path}", "error")
                return

            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            try:
                validated = ProjectExport(**raw_data)
            except ValidationError as e:
                self._update_status("Invalid import format", "error")
                ErrorHandler(
                    file_name=__name__,
                    error=e,
                    cb=lambda e: None,
                )
                return

            # Access validated data
            project_data = validated.project
            tasks_data = validated.tasks

            # Generate new project ID
            new_project_id = str(uuid.uuid4())

            new_project = Project(
                id=new_project_id,
                title=f"{project_data.title} (Imported)",
                description=project_data.description,
                type=project_data.type or "general",
            )

            self.data_provider.save_project(new_project)

            # Import tasks
            imported_count = 0
            original_project = self.data_provider.current_project_id

            self.data_provider.set_current_project(new_project_id)

            for task in tasks_data:
                new_task = Task(
                    id=str(uuid.uuid4()),
                    title=task.title,
                    content=task.content,
                    status=task.status,
                    project_id=new_project_id,
                    is_protected=task.is_protected,
                )

                self.data_provider.save_task(new_task)
                imported_count += 1

            if original_project:
                self.data_provider.set_current_project(original_project)

            self._update_status(
                f"Successfully imported project '{new_project.title}' with {imported_count} tasks",
                "success",
            )

            self.on_submit()
        except json.JSONDecodeError as e:
            self._update_status("Invalid JSON file", "error")
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: None,
            )

        except Exception as e:
            self._update_status("Failed to import", "error")
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: None,
            )

    def _update_status(self, message: str, status_type: str = "info") -> None:
        """Update status message with styling"""
        project_type_container = self.query_one(f"#{EXPORT_PROJECT_RADIO_ID}")

        if status_type == "success":
            project_type_container.border_title = (
                f"{project_type_container.border_title} | ✓ {message}"
            )
        elif status_type == "error":
            project_type_container.border_title = (
                f"{project_type_container.border_title} | ✗ {message}"
            )
        else:
            project_type_container.border_title = (
                f"{project_type_container.border_title} | {message}"
            )
