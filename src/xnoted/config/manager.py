from xnoted.config.loader import ConfigLoader
from xnoted.models.appConfig import AppConfig
from pydantic import ValidationError


class ConfigHandler:
    def __init__(self, path="config.toml") -> None:
        self.loader = ConfigLoader(path)
        self._raw: dict = {}
        self._config: AppConfig
        self.load()

    def load(self):
        self._raw = self.loader.try_load()

        try:
            self._config = AppConfig(**self._raw)
        except ValidationError as e:
            print("Config validation error:")
            print(e)
            self._config = None

    def get(self):
        return self._config
