from textual.containers import Container
from textual.widgets import Input, TextArea, Button
from textual.app import ComposeResult

TEXT = """\
```
def hello(name):
    print("hello" + name)

def goodbye(name):
    print("goodbye" + name)
```
"""


class Form(Container):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="First Name")
        yield TextArea.code_editor(TEXT, language="markdown")
        yield Button("Submit", id="submit", variant="primary")
