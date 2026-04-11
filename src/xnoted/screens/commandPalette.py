from textual.screen import ModalScreen
from collections.abc import Callable
from textual.app import ComposeResult, ActiveBinding
from textual.widgets import Label, ListView, ListItem
from textual.binding import Binding
from xnoted.utils.constants import COMMAND_PALETTE_ID
from dataclasses import dataclass
from typing import TypeAlias
from enum import Enum


ActiveBindingType: TypeAlias = dict[str, ActiveBinding]


class ViewMode(Enum):
    Root = "root"
    Theme = "theme"
    Keys = "keys"
    Screenshot = "screenshot"
    Quit = "quit"


@dataclass
class ThemeValue:
    name: str


ValueType: TypeAlias = ThemeValue | ViewMode | str


@dataclass
class CommandPaletteItemData:
    value: ValueType
    label: str


class CommandPaletteItem(ListItem):
    def __init__(self, *args, value: ValueType, label: str = "", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.value = value
        self.label = label


commands: list[CommandPaletteItemData] = [
    CommandPaletteItemData(value=ViewMode.Keys, label="Keys"),
    CommandPaletteItemData(value=ViewMode.Theme, label="Theme"),
    CommandPaletteItemData(value=ViewMode.Screenshot, label="Screenshot"),
    CommandPaletteItemData(value=ViewMode.Quit, label="Quit"),
]


class CommandPalettes(ListView):
    def __init__(self, bindings: ActiveBindingType, close_app: Callable[[], None]):
        super().__init__(id=COMMAND_PALETTE_ID)
        self.has_task_result = True
        self.close_app = close_app
        self.active_bingings = bindings
        self.mode: ViewMode = ViewMode.Root

    BORDER_TITLE = "Command Palette"

    BINDINGS = [
        Binding("k", "cursor_up", "Cursor up"),
        Binding("j", "cursor_down", "Cursor down"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        for cmd in commands:
            yield CommandPaletteItem(
                Label(self._pad(cmd.label)),
                value=cmd.value,
                label=cmd.label,
            )

    def action_back(self) -> None:
        if self.mode == ViewMode.Root:
            self.app.pop_screen()
        else:
            # go back to main menu
            self.show_root()

    def show_root(self) -> None:
        self.mode = ViewMode.Root
        self.clear()

        for cmd in commands:
            self.append(
                CommandPaletteItem(
                    Label(self._pad(cmd.label)),
                    value=cmd.value,
                    label=cmd.label,
                )
            )

    def _pad(self, value: str) -> str:
        return value.rjust(len(value) + 1)

    def show_theme(self) -> None:
        self.mode = ViewMode.Theme
        self.clear()

        for k, v in self.app.available_themes.items():
            self.append(
                CommandPaletteItem(Label(self._pad(k)), value=ThemeValue(name=v.name))
            )

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        value = getattr(item, "value", None)

        if value == ViewMode.Keys:
            self.show_bindings()
        elif value == ViewMode.Theme:
            self.show_theme()
        elif value == ViewMode.Screenshot:
            self.app.save_screenshot("screenshot.svg")
        elif value == ViewMode.Quit:
            self.close_app()

    def on_list_view_highlighted(self, event: ListView.Selected) -> None:
        item = event.item
        value: ValueType | None = getattr(item, "value", None)

        if isinstance(value, ThemeValue):
            # self.app.register_theme()
            self.app.theme = value.name

    def show_bindings(self) -> None:
        self.clear()
        self.mode = ViewMode.Keys

        for k, v in self.active_bingings.items():
            text = f" {k} → {v.binding.description}"
            yield_item = CommandPaletteItem(Label(self._pad(text)), value=text)
            self.append(yield_item)


class CommandPaletteModal(ModalScreen):
    def __init__(self, bindings: ActiveBindingType):
        super().__init__()
        self.bindings = bindings

    BINDINGS = [
        ("escape", "close", "Close modal"),
    ]

    def compose(self) -> ComposeResult:
        yield CommandPalettes(close_app=self.action_close, bindings=self.bindings)

    def action_close(self) -> None:
        self.app.pop_screen()
