from textual.widget import Widget
from textual.reactive import reactive
from typing import TypeVar, Awaitable
from textual.timer import Timer

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

    frame_index = reactive(0)

    def __init__(self, speed: float = 0.1) -> None:
        super().__init__()
        self.speed = speed
        self._timer: Timer | None = None

    # def on_mount(self) -> None:
    #     self._timer = self.set_interval(self.speed, self._tick)

    def _tick(self) -> None:
        self.frame_index = (self.frame_index + 1) % len(self.FRAMES)

    def render(self) -> str:
        return self.FRAMES[self.frame_index]

    def stop(self) -> None:
        if self._timer:
            self._timer.stop()

    def start(self) -> None:
        if not self._timer:
            self._timer = self.set_interval(self.speed, self._tick)

    async def wrap(self, coro: Awaitable[T]) -> T:
        self.start()
        try:
            return await coro
        finally:
            self.stop()        
