from pydantic import BaseModel, Field


# =========================
# KEYBINDING SECTIONS
# =========================

class GlobalKeybindings(BaseModel):
    create_task: str
    create_project: str
    select_project: str
    import_export: str
    show_readme: str
    scroll_down: str
    scroll_up: str
    pull_sync: str
    push_sync: str
    config_sync: str
    unlock_tasks: str
    command_palette_primary: str
    edit_password: str


class TaskListKeybindings(BaseModel):
    cursor_down: str
    cursor_up: str
    move: str
    select_task: str
    edit_task: str
    copy_task: str
    lock_task: str
    goto_first: str
    goto_last: str
    delete_task: str
    cycle_status_prev: str
    cycle_status_next: str
    search: str

class ProjectListKeybindings(BaseModel):
    cursor_down: str
    cursor_up: str
    edit_project: str
    delete_project: str

class CommandPaletteKeybindings(BaseModel):
    cursor_down: str
    cursor_up: str
    cancel: str

class CopyTaskKeybindings(BaseModel):
    cursor_down: str
    cursor_up: str


class FormKeybindings(BaseModel):
    save: str
    cancel: str


class Keybindings(BaseModel):
    global_: GlobalKeybindings = Field(alias="global")
    task_list: TaskListKeybindings
    project_list: ProjectListKeybindings
    form: FormKeybindings
    command_palette: CommandPaletteKeybindings
    copy_task: CopyTaskKeybindings


# =========================
# THEME
# =========================

class Theme(BaseModel):
    name: str


# =========================
# ROOT CONFIG
# =========================

class AppConfig(BaseModel):
    theme: Theme
    keybindings: Keybindings

    model_config = {
        "extra": "forbid"
    }
