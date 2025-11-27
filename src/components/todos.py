from textual.widgets import ListView, ListItem, Label

class Todos(ListView):
    def __init__(self):
        super().__init__(  # Fixed: Added parentheses to super()
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )

