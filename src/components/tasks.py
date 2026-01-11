from textual.widgets import ListView, ListItem, Label
from src.utils.constants import ICONS
from src.components.body import Body
from src.screens.createTask import CreateTaskModal
from src.screens.confirm import ConfirmModal
from src.utils.database import Database
from textual.binding import Binding
from textual.reactive import reactive


class Tasks(ListView):
    def __init__(self, database=Database):
        super().__init__(id="tasks")
        self.has_task_result = True
        self.database = database

    BINDINGS = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
        Binding("e", "edit_task", "Cursor down", show=False),
        Binding("d", "delete_task", "Cursor down", show=False),
        Binding("left", "change_status('left')", "Change status", show=False),
        Binding("right", "change_status('right')", "Change status", show=False),
    ]

    status_index = reactive(2)

    def on_mount(self):
        self.load_tasks()

    def load_tasks(self) -> None:
        tasks = self.database.load()
        self.clear()
        if tasks:
            for task in tasks:
                title = task.get("title")
                task_id = task.get("id")
                status = task.get("status", 0)
                list_item = ListItem(Label(f"{ICONS[status].get('icon')} {title}"))
                list_item.task_id = task_id
                list_item.status = status
                self.append(list_item)
        else:
            # Display Readme as Welcome
            if self.database.is_empty():
                body_widget: Body = self.app.query_one(Body)
                body_widget.welcome()
                self.append(ListItem(Label("No tasks yet")))
            else:
                self.append(ListItem(Label("No tasks yet")))

    def refresh_tasks(self):
        """Public method to refresh the task list"""
        self.load_tasks()

    def quick_search(self, text: str) -> None:
        """Public method to quick search the task list"""
        tasks = self.database.load()

        if not text:
            self.has_task_result = True

        if not self.has_task_result:
            return

        self.clear()

        if tasks and self.has_task_result:
            found_any = False
            for task in tasks:
                title = task.get("title")
                if text.lower() in title.lower():
                    task_id = task.get("id")
                    list_item = ListItem(Label(f"● {title}"))
                    list_item.task_id = task_id
                    self.append(list_item)
                    found_any = True

            if not found_any:
                self.has_task_result = False
                self.append(ListItem(Label("No matching tasks")))
        else:
            self.append(ListItem(Label("No tasks yet")))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and hasattr(event.item, "task_id"):
            # Display the highlighted task
            task_id = event.item.task_id
            body_widget = self.app.query_one(Body)
            body_widget.show_task(task_id)

    def action_edit_task(self):
        child = self.highlighted_child

        if child and hasattr(child, "task_id"):
            tasks = self.database.load()
            task_id = child.task_id

            for task in tasks:
                if task.get("id") == task_id:
                    title = task.get("title")
                    content = task.get("content")
                    self.app.push_screen(
                        CreateTaskModal(
                            database=self.database,
                            title=title,
                            content=content,
                            editing=True,
                            task_id=task_id,
                        )
                    )
                    break

    def action_change_status(self, direction: str):
        child = self.highlighted_child
        if child is None or not hasattr(child, "task_id"):
            return

        # Get current status for this specific item
        current_status = getattr(child, "status", 0)

        # Update status index for this item
        if direction == "right" and current_status < len(ICONS) - 1:
            new_status = current_status + 1
        elif direction == "left" and current_status > 0:
            new_status = current_status - 1
        elif direction == "left" and current_status == 0:
            new_status = len(ICONS) - 1
        else:
            new_status = 0

        # Update only the highlighted item's label
        label = child.query_one(Label)
        title = label.content.split(" ", 1)[1]
        label.update(f"{ICONS[new_status].get('icon')} {title}")
        child.status = new_status
        task = self.database.get_task(child.task_id)

        new_data = {
            "title": task["title"],
            "content": task["content"],
            "status": new_status,
        }

        self.database.update_task(child.task_id, new_data)

    def action_delete_task(self):
        child: ListItem = self.highlighted_child

        if child and hasattr(child, "task_id"):
            task_id = child.task_id

            def on_confirm():
                self.database.delete_task(task_id)
                self.refresh_tasks()

            self.app.push_screen(ConfirmModal(on_confirm=on_confirm))
