from xnoted.config.loader import ConfigLoader
from xnoted.models.appConfig import AppConfig
from pydantic import ValidationError
from xnoted.utils.deepMerge import deep_merge


class ConfigHandler:
    def __init__(self, path="config.toml") -> None:
        self.loader = ConfigLoader(path)
        self._raw: dict = {}
        self._custom_raw: dict = {}
        self._config: AppConfig | None = None

        self.load()

    def load(self):
        self._raw = self.loader.try_load() or {}
        self._custom_raw = self.loader.load_custom() or {}

        merged = deep_merge(self._raw, self._custom_raw)

        try:
            self._config = AppConfig(**merged)
        except ValidationError as e:
            print("Config validation error:")
            print(e)
            self._config = None

    def get(self):
        return self._config
