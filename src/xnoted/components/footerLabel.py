from typing import Iterator
from textual.widgets import Static, Label
from xnoted.utils.database import Database

class FooterLabel(Static):        
    def __init__(self, database: Database):
        super().__init__()
        self.database = database
    
    def compose(self) -> Iterator[Label]:
        yield Label(
            "Move down: j | Move up: k | Edit task: e | Copy task: c | Delete task: d | "
            "Previous status: ← | Next status: → | Body down: Ctrl+d | "
            "Body up: Ctrl+u | Search: /",
            id="help-text"
        )
    
