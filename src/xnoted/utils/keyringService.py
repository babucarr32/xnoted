import keyring
from typing import Optional
from dataclasses import dataclass


SERVICE_NAME = "xnoted"


@dataclass(frozen=True)
class Credentials:
    url: str
    db_name: Optional[str] = None


class DBKeyring:
    URL_KEY = "db_url"
    NAME_KEY = "db_name"

    def set_credentials(self, data: Credentials) -> None:
        keyring.set_password(SERVICE_NAME, self.URL_KEY, data.url)

        if data.db_name:
            keyring.set_password(SERVICE_NAME, self.NAME_KEY, data.db_name)

    def get_credentials(self) -> Optional[Credentials]:
        url = keyring.get_password(SERVICE_NAME, self.URL_KEY)
        db_name = keyring.get_password(SERVICE_NAME, self.NAME_KEY)

        if not url:
            return None

        return Credentials(url=url, db_name=db_name)

    def clear_credentials(self) -> None:
        for key in (self.URL_KEY, self.NAME_KEY):
            try:
                keyring.delete_password(SERVICE_NAME, key)
            except keyring.errors.PasswordDeleteError:
                pass
