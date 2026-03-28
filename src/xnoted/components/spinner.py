from typing import Awaitable, TypeVar

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Label

T = TypeVar("T")


class Spinner(Widget):
    DEFAULT_CSS = """
    Spinner {
        width: auto;
        height: 1;
        content-align: center middle;
    }
    """
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    frame_index: reactive[int] = reactive(0)
    is_spinning: reactive[bool] = reactive(False)
    text: reactive[str] = reactive("")

    def __init__(self, speed: float = 0.1) -> None:
        super().__init__()
        self.speed = speed
        self._timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Label("", id="spinner-label")

    def _get_label(self) -> Label:
        return self.query_one("#spinner-label", Label)

    def _update_label(self) -> None:
        if not self.is_spinning:
            self._get_label().update("")
        else:
            frame = self.FRAMES[self.frame_index]
            self._get_label().update(f"{frame} {self.text}".rstrip())

    def watch_frame_index(self) -> None:
        self._update_label()

    def watch_is_spinning(self) -> None:
        self._update_label()

    def watch_text(self) -> None:
        self._update_label()

    def _tick(self) -> None:
        self.frame_index = (self.frame_index + 1) % len(self.FRAMES)

    def start(self, text: str = "") -> None:
        self.text = text
        if not self._timer:
            self._timer = self.set_interval(self.speed, self._tick)
            self.is_spinning = True

    def stop(self) -> None:
        if self._timer:
            self._timer.stop()
            self._timer = None
            self.is_spinning = False

    async def wrap(self, coro: Awaitable[T], text: str = '') -> T:
        self.start(text)
        try:
            return await coro
        finally:
            self.stop()
