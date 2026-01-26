from textual.widgets import Static, Label, Input
from textual.reactive import reactive
from src.utils.database import Database

class FooterLabel(Static):    
    is_searching = reactive(False)
    
    def __init__(self, database: Database):
        super().__init__()
        self.database = database
    
    def compose(self):
        self.log(f"Composing with is_searching={self.is_searching}")
        if not self.is_searching:
            yield Label(
                "Move down: j | Move up: k | Edit task: e | Delete task: d | "
                "Previous status: ← | Next status: → | Body down: Ctrl+d | "
                "Body up: Ctrl+u | Search: /",
                id="help-text"
            )
        else:
            yield Input(
                placeholder="Search tasks...",
                id="search-input"
            )
    
    async def watch_is_searching(self, old_value: bool, new_value: bool):
        """Called automatically when is_searching changes"""
        self.log(f"is_searching changed from {old_value} to {new_value}")
        
        # Remove all children
        await self.query("*").remove()
        
        # Mount the appropriate widget
        if new_value:
            search_input = Input(placeholder="Search tasks...", id="search-input")
            await self.mount(search_input)
            search_input.focus()
        else:
            await self.mount(Label(
                "Move down: j | Move up: k | Edit task: e | Delete task: d | "
                "Previous status: ← | Next status: → | Body down: Ctrl+d | "
                "Body up: Ctrl+u | Search: /",
                id="help-text"
            ))
        
    def toggle_search(self):
        """Toggle between help text and search input"""
        self.log("Toggling search, current:", self.is_searching)
        self.is_searching = not self.is_searching
