from types import SimpleNamespace
from typing import Any


class Settings(SimpleNamespace):
    NAME_HEADER = 'Auto Wrinkle Map'
    EXTENSION_ID = NAME_HEADER.replace(' ', '_').lower()
    INDENT = 20


settings = Settings()
