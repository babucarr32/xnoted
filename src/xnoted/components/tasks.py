import uuid
from textual.widgets import ListView, ListItem, Label
from xnoted.utils.constants import (
    ICONS,
    FOOTER_ID,
    TASKS_ID,
    PROJECT_TASK_TYPE_ID,
    TASK_LABEL_ID,
)
from xnoted.utils.helpers import mask
from xnoted.components.body import Body
from xnoted.screens.selectProjects import SelectProjectModal
from xnoted.screens.copyTask import CopyTaskModal
from xnoted.screens.confirm import ConfirmModal
from xnoted.screens.createPassword import CreatePasswordModal
from typing import cast
from dataclasses import dataclass
from xnoted.database.dataProvider import DataProvider, Task
from textual.binding import Binding
from textual.reactive import reactive
from xnoted.utils.logger import get_logger
from xnoted.components.footer import Footer

logger = get_logger(__name__)


@dataclass
class GetLabelArg:
    status: int
    title: str
    is_protected: bool


class TaskLabel(Label):
    def __init__(self, *args, task_id: str = "", status: int = 0, **kwargs):
        super().__init__(*args, **kwargs, id=TASK_LABEL_ID)
        self.task_id = task_id
        self.status = status


class TaskItem(ListItem):
    def __init__(self, *args, task_id: str, status: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_id = task_id
        self.status = status


class Tasks(ListView):
    def __init__(self, data_provider=DataProvider):
        super().__init__(id=TASKS_ID)
        self.has_task_result = True
        self.data_provider = data_provider

    BINDINGS = [
        Binding("m", "move", "Move task"),
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
        Binding("/", "search", "Search", show=False),
        Binding("e", "edit_task", "Cursor down", show=False),
        Binding("l", "lock_task", "Lock down", show=False),
        Binding("c", "copy_task", "Copy down", show=False),
        Binding("d", "delete_task", "Delete down", show=False),
        Binding("left", "change_status('left')", "Change status", show=False),
        Binding("right", "change_status('right')", "Change status", show=False),
    ]

    last_matched_search: reactive[str] = reactive("")

    def on_mount(self) -> None:
        self.load_tasks()

    def _handle_mask(self, text: str, is_protected: bool) -> str:
        if is_protected:
            return mask(text)
        return text

    def _get_label(self, arg: GetLabelArg) -> str:
        return f"{ICONS[arg.status].get('icon')} {self._handle_mask(arg.title, arg.is_protected)}"

    def load_tasks(self) -> None:
        tasks = self.data_provider.load_tasks(self.data_provider.current_project_id)
        self.clear()
        if tasks:
            for task in tasks:
                if self.data_provider.project_type == PROJECT_TASK_TYPE_ID:
                    label_arg = GetLabelArg(
                        status=task.status,
                        title=task.title,
                        is_protected=task.is_protected == 1,
                    )
                    label = self._get_label(label_arg)
                else:
                    label = self._handle_mask(task.title, task.is_protected)

                list_item = TaskItem(
                    TaskLabel(label), task_id=task.id, status=task.status
                )
                self.append(list_item)
        else:
            if self.data_provider.is_empty():
                self.append(ListItem(Label("No tasks yet")))

    def refresh_tasks(self) -> None:
        """Public method to refresh the task list"""
        self.load_tasks()

    def quick_search(self, text: str) -> None:
        """Public method to quick search the task list"""
        tasks = self.data_provider.load_tasks(self.data_provider.current_project_id)
        search_text = text.lower()

        if not text or self.last_matched_search == search_text:
            self.has_task_result = True

        if not self.has_task_result:
            return

        self.clear()

        if tasks and self.has_task_result:
            found_any = False
            for task in tasks:
                if search_text in task.title.lower():
                    label_arg = GetLabelArg(
                        status=task.status,
                        title=task.title,
                        is_protected=task.is_protected,
                    )
                    label = self._get_label(label_arg)
                    list_item = TaskItem(
                        TaskLabel(label), task_id=task.id, status=task.status
                    )
                    self.append(list_item)
                    found_any = True

            if not found_any:
                self.has_task_result = False
                self.append(ListItem(Label("No matching tasks")))
            else:
                self.last_matched_search = search_text
        else:
            self.append(ListItem(Label("No tasks yet")))

    def _display_task(self, task_id: str) -> None:
        body_widget = self.app.query_one(Body)
        body_widget.show_task(task_id)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and hasattr(event.item, "task_id"):
            # Display the highlighted task
            task_id = event.item.task_id
            self._display_task(task_id)

    def action_edit_task(self) -> None:
        from xnoted.screens.createTask import CreateTaskModal

        child = self.highlighted_child

        if child and hasattr(child, "task_id"):
            task_id = child.task_id
            task = self.data_provider.get_task(task_id)

            if not task:
                logger.error(f"Task with id {task_id} not found")
                return None

            self.app.push_screen(
                CreateTaskModal(
                    data_provider=self.data_provider,
                    title=task.title,
                    content=task.content,
                    editing=True,
                    task_id=task.id,
                )
            )

    def action_change_status(self, direction: str) -> None:
        if self.data_provider.project_type != PROJECT_TASK_TYPE_ID:
            return

        child: TaskLabel | None = cast(TaskLabel | None, self.highlighted_child)
        if child is None or not hasattr(child, "task_id"):
            return

        task = self.data_provider.get_task(task_id=child.task_id)

        if not task:
            logger.error(f"Task with id {task.id} not found")
            return None

        # Update status index for this item
        if direction == "right" and task.status < len(ICONS) - 1:
            new_status = task.status + 1
        elif direction == "left" and task.status > 0:
            new_status = task.status - 1
        elif direction == "left" and task.status == 0:
            new_status = len(ICONS) - 1
        else:
            new_status = 0

        # Update only the highlighted item's label
        label = cast(TaskLabel, child.query_one(f"#$TASK_LABEL_ID"))

        label_arg = GetLabelArg(
            status=new_status,
            title=task.title,
            is_protected=task.is_protected,
        )

        label.update(self._get_label(label_arg))
        child.status = new_status

        new_data = Task(
            id=task.id,
            title=task.title,
            content=task.content,
            status=new_status,
            is_protected=task.is_protected,
            project_id=task.project_id,
        )

        self.data_provider.update_task(task.id, new_data)

    def action_delete_task(self) -> None:
        child: TaskItem | None = cast(TaskItem | None, self.highlighted_child)

        if child and hasattr(child, "task_id"):
            task_id = child.task_id

            def on_confirm():
                self.data_provider.delete_task(task_id)
                self.refresh_tasks()

            self.app.push_screen(ConfirmModal(on_confirm=on_confirm))

    def action_lock_task(self) -> None:
        child: TaskItem | None = cast(TaskItem | None, self.highlighted_child)

        if child and hasattr(child, "task_id"):
            label_widget = cast(TaskLabel, child.get_child_by_id(TASK_LABEL_ID))

            task_id = child.task_id
            task = self.data_provider.get_task(task_id)

            new_data = Task(
                id=task.id,
                title=task.title,
                content=task.content,
                status=task.status,
                is_protected=1,
                project_id=task.project_id,
            )

            def on_password_created() -> None:
                self.data_provider.update_task(child.task_id, new_data)

            if not self.data_provider.has_password:
                self.app.push_screen(
                    CreatePasswordModal(
                        data_provider=self.data_provider,
                        on_password_created=on_password_created,
                    )
                )
            else:
                self.data_provider.update_task(child.task_id, new_data)
                label_arg = GetLabelArg(
                    status=new_data.status,
                    title=new_data.title,
                    is_protected=new_data.is_protected == 1,
                )
                label = self._get_label(label_arg)
                label_widget.update(label)
                self._display_task(new_data.id)

    def action_copy_task(self) -> None:
        child: TaskItem | None = cast(TaskItem | None, self.highlighted_child)

        if child and hasattr(child, "task_id"):
            task_id = child.task_id
            self.app.push_screen(
                CopyTaskModal(data_provider=self.data_provider, item_id=task_id)
            )

    def action_search(self) -> None:
        footer: Footer = cast(Footer, self.app.query_one(f"#{FOOTER_ID}"))
        footer.toggle_search()

    def action_move(self) -> None:
        child: TaskItem | None = cast(TaskItem | None, self.highlighted_child)

        if child and hasattr(child, "task_id"):
            task_id = child.task_id
            cached_project_id = self.data_provider.current_project_id

            def on_select(project_id: str):
                if project_id:
                    self.data_provider.set_current_project(project_id)
                    # Save the highlighted task to the selected project
                    task = self.data_provider.get_task(task_id)

                    if task:
                        data = Task(
                            id=str(uuid.uuid4()),
                            title=task.title,
                            content=task.content,
                            project_id=task.project_id,
                            is_protected=task.is_protected,
                            status=task.status,
                        )

                        try:
                            self.data_provider.save_task(data)
                            # Then delete the task
                            self.data_provider.delete_task(task_id)
                            # Set the project id back
                            self.data_provider.set_current_project(cached_project_id)
                            self.refresh_tasks()
                        except Exception as e:
                            logger.error(f"Unable to move task {e}")

            self.app.push_screen(
                SelectProjectModal(
                    data_provider=self.data_provider,
                    on_select=on_select,
                    _border_title="Move to",
                )
            )
