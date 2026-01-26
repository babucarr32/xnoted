from textual.widgets import Static
from src.utils.database import Database
from src.components.footerLabel import FooterLabel


class Footer(Static):
    def __init__(self, database: Database):
        super().__init__()
        self.database = database

    def compose(self):
        yield FooterLabel(database=self.database)
