import os
from types import SimpleNamespace


class Settings(SimpleNamespace):
    NAME_HEADER = 'Auto Wrinkle Map'
    EXTENSION_ID = NAME_HEADER.replace(' ', '_').lower()
    ICONS_PATH = os.path.join(os.path.dirname(__file__), 'icons')
    INDENT = 20


settings = Settings()
