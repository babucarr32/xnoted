from xnoted.errors.errorHandler import ErrorHandler
from dataclasses import replace
from textual.widgets import ListView, ListItem, Label
from xnoted.utils.constants import (
    ICONS,
    FOOTER_ID,
    TASKS_ID,
    PROJECT_TASK_TYPE_ID,
    PROJECT_OTHER_TYPE_ID,
    TASK_LABEL_ID,
    ERROR_TITLE,
    RIGHT_DIRECTION,
    LEFT_DIRECTION,
)
from xnoted.utils.helpers import mask
from xnoted.components.body import Body
from xnoted.screens.enterPassword import EnterPasswordModal
from xnoted.screens.selectProjects import SelectProjectModal
from xnoted.sync.syncProvider import SyncStatus
from xnoted.screens.copyTask import CopyTaskModal
from xnoted.screens.confirm import ConfirmModal
from xnoted.screens.createPassword import CreatePasswordModal
from typing import cast, Callable
from dataclasses import dataclass
from xnoted.database.dataProvider import DataProvider, Task, ProtectionStatus
from textual.reactive import reactive
from xnoted.utils.logger import get_logger
from xnoted.components.footer import Footer
from xnoted.config.manager import ConfigHandler


logger = get_logger(__name__)


@dataclass
class GetLabelArg:
    status: int
    title: str
    is_protected: bool
    project_type: str


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
    def __init__(
        self, data_provider: DataProvider, config_handler: ConfigHandler
    ) -> None:
        super().__init__(id=TASKS_ID)
        self.has_task_result = True
        self.data_provider = data_provider
        self.tasks: list[Task] = []
        self.config_handler = config_handler

    last_matched_search: reactive[str] = reactive("")

    def on_mount(self) -> None:
        config = self.config_handler.get()
        kb = config.keybindings.task_list

        self._bindings.bind(keys=kb.move, action="move", description="Move task")
        self._bindings.bind(
            keys=kb.select_task, action="select_cursor", description="Select"
        )
        self._bindings.bind(
            keys=kb.cursor_up, action="cursor_up", description="Cursor up"
        )
        self._bindings.bind(
            keys=kb.cursor_down, action="cursor_down", description="Cursor down"
        )
        self._bindings.bind(keys=kb.search, action="search", description="Search")
        self._bindings.bind(
            keys=kb.edit_task, action="edit_task", description="Cursor down"
        )
        self._bindings.bind(
            keys=kb.lock_task, action="lock_task", description="Lock down"
        )
        self._bindings.bind(
            keys=kb.copy_task, action="copy_task", description="Copy down"
        )
        self._bindings.bind(
            keys=kb.delete_task, action="delete_task", description="Delete down"
        )
        self._bindings.bind(
            keys=kb.goto_last, action="goto_last", description="Last item"
        )
        self._bindings.bind(
            keys=kb.goto_first, action="goto_first", description="First item"
        )
        self._bindings.bind(
            kb.cycle_status_prev, f"change_status('{LEFT_DIRECTION}')", "Change status"
        )
        self._bindings.bind(
            kb.cycle_status_next, f"change_status('{RIGHT_DIRECTION}')", "Change status"
        )

        self.load_tasks()

    def focus_fist_child(self):
        if self.children:
            self.index = 0
            self.scroll_visible

    def focus_container_and_fist_child(self):
        self.focus_fist_child()
        self.focus()

    def action_cursor_up(self) -> None:
        count = len(self)
        if count == 0:
            return

        if isinstance(self.index, int):
            new_index = (self.index - 1) % count
            self.index = new_index
            self.scroll_to_widget(self.children[new_index])

    def action_cursor_down(self) -> None:
        count = len(self)
        if count == 0:
            return

        if isinstance(self.index, int):
            new_index = (self.index + 1) % count
            self.index = new_index
            self.scroll_to_widget(self.children[new_index])

    def action_goto_last(self) -> None:
        last = len(self) - 1
        self.index = last
        self.scroll_to_widget(self.children[last], animate=False)

    def action_goto_first(self) -> None:
        self.index = 0
        self.scroll_to_widget(self.children[0], animate=False)

    def _handle_mask(self, text: str, is_protected: bool) -> str:
        return mask() if is_protected else text

    def _get_label(self, arg: GetLabelArg) -> str:
        if arg.project_type == PROJECT_OTHER_TYPE_ID:
            return self._handle_mask(arg.title, arg.is_protected)

        return f"{ICONS[arg.status].get('icon')} {self._handle_mask(arg.title, arg.is_protected)}"

    def _project_with_id_not_found(self, project_id: str) -> None:
        ErrorHandler(
            file_name=__name__,
            error=None,
            cb=lambda e: self.notify(
                f"Project with id {project_id} not found",
                title=ERROR_TITLE,
                severity=e.severity,
            ),
        )

    def load_tasks(self) -> None:
        try:
            if not self.data_provider.current_project_id:
                self._project_with_id_not_found(
                    cast(str, self.data_provider.current_project_id)
                )
                return None

            self.tasks = self.data_provider.get_tasks(
                self.data_provider.current_project_id
            )

            self.clear()
            self.call_after_refresh(self.focus_fist_child)

            project = self.data_provider.get_project(
                self.data_provider.current_project_id
            )

            if not project:
                self._project_with_id_not_found(
                    cast(str, self.data_provider.current_project_id)
                )
                return None

            if not self.tasks or not len(self.tasks):
                self.append(ListItem(Label("No tasks yet")))
                return

            for task in self.tasks:
                if self.data_provider.project_type == PROJECT_TASK_TYPE_ID:
                    label_arg = GetLabelArg(
                        status=task.status,
                        title=task.title,
                        is_protected=task.is_protected
                        == ProtectionStatus.PROTECTED.value,
                        project_type=project.type,
                    )
                    label = self._get_label(label_arg)
                else:
                    label = self._handle_mask(
                        task.title,
                        task.is_protected == ProtectionStatus.PROTECTED.value,
                    )

                list_item = TaskItem(
                    TaskLabel(label), task_id=task.id, status=task.status
                )
                self.append(list_item)
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def refresh_tasks(self) -> None:
        """Public method to refresh the task list"""
        self.load_tasks()

    def quick_search(self, text: str) -> None:
        """Public method to quick search the task list"""
        try:
            search_text = text.lower()

            if not text or self.last_matched_search == search_text:
                self.has_task_result = True

            if not self.has_task_result:
                return

            if not search_text:
                self.load_tasks()
                return

            self.clear()

            if not self.data_provider.current_project_id:
                self._project_with_id_not_found(
                    cast(str, self.data_provider.current_project_id)
                )
                return

            if len(self.tasks) and self.has_task_result:
                found_any = False
                project = self.data_provider.get_project(
                    self.data_provider.current_project_id
                )

                if not project:
                    self._project_with_id_not_found(
                        cast(str, self.data_provider.current_project_id)
                    )
                    return

                for task in self.tasks:
                    if search_text in task.title.lower() and not task.is_protected:
                        label_arg = GetLabelArg(
                            status=task.status,
                            title=task.title,
                            is_protected=task.is_protected
                            == ProtectionStatus.PROTECTED.value,
                            project_type=project.type,
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
                return

            self.append(ListItem(Label("No tasks yet")))
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def _display_task(self, task_id: str) -> None:
        body_widget: Body = self.app.query_one(Body)
        body_widget.show_task(task_id)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        try:
            if event.item and hasattr(event.item, "task_id"):
                # Display the highlighted task
                task_id = event.item.task_id
                self._display_task(task_id)
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def action_edit_task(self) -> None:
        try:
            from xnoted.screens.createTask import CreateTaskModal

            child = self.highlighted_child

            if child and hasattr(child, "task_id"):
                task_id = child.task_id
                task = self.data_provider.get_task(task_id)

                if not task:
                    self.notify(
                        f"Task with id {task_id} not found",
                        title=ERROR_TITLE,
                        severity="error",
                    )
                    logger.error(f"Task with id {task_id} not found")
                    return None

                self.app.push_screen(
                    CreateTaskModal(
                        data_provider=self.data_provider,
                        editing=True,
                        task_id=task.id,
                        config_handler=self.config_handler,
                    )
                )
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def action_change_status(self, direction: str) -> None:
        try:
            if self.data_provider.project_type != PROJECT_TASK_TYPE_ID:
                return

            child: TaskLabel | None = cast(TaskLabel | None, self.highlighted_child)
            if child is None or not hasattr(child, "task_id"):
                return

            task = self.data_provider.get_task(task_id=child.task_id)

            if not task:
                ErrorHandler(
                    file_name=__name__,
                    error=None,
                    cb=lambda e: self.notify(
                        f"Task with id {child.task_id} not found",
                        title=ERROR_TITLE,
                        severity=e.severity,
                    ),
                )
                return

            if not task:
                logger.error(f"Task with id {task.id} not found")
                self.notify(
                    f"Task with id {task.id} not found",
                    title=ERROR_TITLE,
                    severity="error",
                )
                return None

            # Update status index for this item
            if direction == RIGHT_DIRECTION and task.status < len(ICONS) - 1:
                new_status = task.status + 1
            elif direction == LEFT_DIRECTION and task.status > 0:
                new_status = task.status - 1
            elif direction == LEFT_DIRECTION and task.status == 0:
                new_status = len(ICONS) - 1
            else:
                new_status = 0

            # Update only the highlighted item's label
            label = cast(TaskLabel, child.query_one(f"#{TASK_LABEL_ID}"))

            label_arg = GetLabelArg(
                status=new_status,
                title=task.title,
                is_protected=task.is_protected == ProtectionStatus.PROTECTED.value,
                project_type=self.data_provider.project_type,
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
                sync_status=SyncStatus.PENDING_EDIT.value,
            )

            self.data_provider.update_task(task.id, new_data)
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def action_delete_task(self) -> None:
        child: TaskItem | None = cast(TaskItem | None, self.highlighted_child)

        if not child or not hasattr(child, "task_id"):
            return

        task_id = child.task_id

        def on_confirm():
            try:
                self.data_provider.delete_task(task_id)
                self.refresh_tasks()
            except Exception as e:
                ErrorHandler(
                    file_name=__name__,
                    error=e,
                    cb=lambda e: self.notify(
                        e.content, title=e.title, severity=e.severity
                    ),
                )

        self.app.push_screen(
            ConfirmModal(on_confirm=on_confirm, config_handler=self.config_handler)
        )

    def _update_task_state(
        self,
        *,
        task_id: str,
        label_widget: Label,
        transform: Callable[[str], Task],
        is_protected: bool,
    ) -> None:
        task = transform(task_id)
        updated = replace(task, sync_status=SyncStatus.PENDING_EDIT.value)

        self.data_provider.update_task(task.id, updated)

        if not self.data_provider.current_project_id:
            self._project_with_id_not_found(
                cast(str, self.data_provider.current_project_id)
            )
            return

        project = self.data_provider.get_project(self.data_provider.current_project_id)

        if not project:
            self._project_with_id_not_found(
                cast(str, self.data_provider.current_project_id)
            )
            return

        label = self._get_label(
            GetLabelArg(
                status=updated.status,
                title=updated.title,
                project_type=project.type,
                is_protected=is_protected,
            )
        )

        label_widget.update(label)
        self._display_task(updated.id)

    def lock_task(self, *, task_id: str, label_widget: Label) -> None:
        def proceed():
            self._update_task_state(
                task_id=task_id,
                label_widget=label_widget,
                transform=self.data_provider.encrypt_task,
                is_protected=True,
            )

        if not self.data_provider.has_password:
            self.app.push_screen(
                CreatePasswordModal(
                    data_provider=self.data_provider,
                    config_handler=self.config_handler,
                    on_password_created=proceed,
                )
            )
            return

        proceed()

    def unlock_task(self, *, task_id: str, label_widget: Label) -> None:
        def on_password_valid():
            self._update_task_state(
                task_id=task_id,
                label_widget=label_widget,
                transform=self.data_provider.decrypt_task,
                is_protected=False,
            )

        self.app.push_screen(
            EnterPasswordModal(
                data_provider=self.data_provider,
                on_password_valid=on_password_valid,
                config_handler=self.config_handler,
            )
        )

    def _get_active_task_context(self) -> tuple[str, TaskLabel] | None:
        child = cast(TaskItem | None, self.highlighted_child)

        if not child or not hasattr(child, "task_id"):
            self.notify(
                "Task item not found", title="Something went wrong", severity="error"
            )
            logger.error("Task item not found")
            return None

        label_widget = cast(TaskLabel, child.get_child_by_id(TASK_LABEL_ID))
        return child.task_id, label_widget

    def action_lock_task(self) -> None:
        try:
            ctx = self._get_active_task_context()
            if not ctx:
                return

            task_id, label_widget = ctx
            task = self.data_provider.get_task(task_id)

            if not task:
                self.notify(
                    f"Task with id {task_id} not found",
                    title="Something went wrong",
                    severity="error",
                )
                logger.error(f"Task with id {task_id} not found")
                return

            if task.is_protected:
                self.unlock_task(task_id=task_id, label_widget=label_widget)
                return

            self.lock_task(task_id=task_id, label_widget=label_widget)

        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def action_copy_task(self) -> None:
        try:
            child: TaskItem | None = cast(TaskItem | None, self.highlighted_child)

            if child and hasattr(child, "task_id"):
                task_id = child.task_id
                self.app.push_screen(
                    CopyTaskModal(
                        data_provider=self.data_provider,
                        item_id=task_id,
                        config_handler=self.config_handler,
                    )
                )
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def action_search(self) -> None:
        try:
            footer: Footer = cast(Footer, self.app.query_one(f"#{FOOTER_ID}"))
            footer.toggle_search()
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )

    def action_move(self) -> None:
        try:
            child: TaskItem | None = cast(TaskItem | None, self.highlighted_child)

            if not child or not hasattr(child, "task_id"):
                return

            if not self.data_provider.current_project_id:
                self._project_with_id_not_found(
                    cast(str, self.data_provider.current_project_id)
                )
                return

            task_id = child.task_id
            cached_project_id = self.data_provider.current_project_id

            def on_select(project_id: str):
                if not project_id:
                    return

                self.data_provider.set_current_project(project_id)
                # Save the highlighted task to the selected project
                task = self.data_provider.get_task(task_id)

                if not task:
                    return

                data = Task(
                    id="str(uuid.uuid4())",
                    title=task.title,
                    content=task.content,
                    project_id=task.project_id,
                    is_protected=task.is_protected,
                    status=task.status,
                )

                self.data_provider.save_task(data)
                # Then delete the task
                self.data_provider.delete_task(task_id)
                # Set the project id back
                self.data_provider.set_current_project(cached_project_id)
                self.refresh_tasks()

            self.app.push_screen(
                SelectProjectModal(
                    data_provider=self.data_provider,
                    on_select=on_select,
                    _border_title="Move to",
                    config_handler=self.config_handler,
                )
            )
        except Exception as e:
            ErrorHandler(
                file_name=__name__,
                error=e,
                cb=lambda e: self.notify(e.content, title=e.title, severity=e.severity),
            )
