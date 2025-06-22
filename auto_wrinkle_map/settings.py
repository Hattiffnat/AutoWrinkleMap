from types import SimpleNamespace
from typing import Any


class Settings(SimpleNamespace):
    NAME_HEADER = 'Auto Wrinkle Map'
    NAME_DEV = NAME_HEADER.replace(' ', '_').lower()
    INDENT = 20


settings = Settings()
