from textual.containers import Container
from textual.widgets import Input, TextArea, Button
from textual.app import ComposeResult
from src.utils.storage import Storage

TEXT = """\
```
def hello(name):
    print("hello" + name)

def goodbye(name):
    print("goodbye" + name)
```
"""

TITLE_ID = "title"
CONTENT_ID = "content"
DB_PATH = "db.json"

class Form(Container):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="First Name", id=TITLE_ID)
        yield TextArea.code_editor(TEXT, language="markdown", id=CONTENT_ID)
        yield Button("Submit", id="submit", variant="primary")

    # def on_input_changed(self, event: Input.Changed):
    #     self.log(f"Input changed: {event.value}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        storage = Storage(DB_PATH)
        title = self.query_one(f"#{TITLE_ID}").value
        content = self.query_one(f"#{CONTENT_ID}").text
        data = {
            "title": title,
            "content": content
        }

        if storage.is_storage_exist():
            storage.append(data)
        else:
            storage.save(data)

        self.log(f"Title: {title}")
        self.log(f"Content: {content}")
