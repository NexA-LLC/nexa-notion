from typing import Dict, Any, TypedDict

class DatabaseConfig(TypedDict):
    rootPageId: str

class NotionConfig(TypedDict):
    token: str
    databases: Dict[str, DatabaseConfig]

class MarkdownConfig(TypedDict):
    managementDir: str
    developmentDir: str

class SyncConfig(TypedDict):
    watchMode: bool

class Config(TypedDict):
    notion: NotionConfig
    markdown: MarkdownConfig
    sync: SyncConfig 