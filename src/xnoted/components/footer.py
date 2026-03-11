from textual.widgets import Static
from xnoted.database.dataProvider import DataProvider
from textual.reactive import reactive
from xnoted.components.footerLabel import FooterLabel
from xnoted.components.footerSearch import FooterSearch
from xnoted.utils.constants import FOOTER_ID
from typing import Iterator


class Footer(Static):
    is_searching = reactive(False, recompose=True)

    def __init__(self, data_provider: DataProvider):
        super().__init__(id=FOOTER_ID)
        self.data_provider = data_provider

    def compose(self) -> Iterator[FooterLabel | FooterSearch]:
        if not self.is_searching:
            yield FooterLabel()
        else:
            yield FooterSearch(
                data_provider=self.data_provider, toggle_search=self.toggle_search
            )

    def toggle_search(self) -> None:
        """Toggle between help text and search input"""
        self.is_searching = not self.is_searching
