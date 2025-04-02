import os
from typing import Dict, Any, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

from ..notion.client import NotionClient
from ..notion.block import BlockConverter
from ..types import Config

console = Console()

class MarkdownHandler(FileSystemEventHandler):
    def __init__(self, manager: 'SyncManager'):
        self.manager = manager

    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            self.manager.handle_markdown_change(event.src_path)

class SyncManager:
    def __init__(self, config: Config):
        self.config = config
        self.notion = NotionClient(config["notion"]["token"])
        self.page_map: Dict[str, str] = {}  # UUID -> filePath
        self.observer = Observer()

    async def sync_from_notion(self):
        """NotionからMarkdownへの同期"""
        try:
            for db_name, db_config in self.config["notion"]["databases"].items():
                console.print(f"[bold blue]データベース {db_name} の同期を開始[/]")
                await self.sync_database(db_name, db_config)
        except Exception as e:
            console.error("Notionからの同期中にエラーが発生しました")
            console.error(e)
            raise

    async def sync_database(self, db_name: str, db_config: Dict[str, Any]):
        """データベースの同期"""
        root_page = self.notion.get_page(db_config["rootPageId"])
        blocks = self.notion.get_page_blocks(db_config["rootPageId"])
        
        # ページの内容をMarkdownに変換
        markdown = BlockConverter.blocks_to_markdown(blocks)
        
        # ファイルパスを生成
        file_name = f"{root_page['properties']['title']['title'][0]['plain_text']}.md"
        file_path = os.path.join(self.config["markdown"][f"{db_name}Dir"], file_name)
        
        # メタデータを追加
        content = self.add_metadata(markdown, {
            "notionId": root_page["id"],
            "lastSynced": "now",
        })
        
        # ファイルを保存
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.page_map[root_page["id"]] = file_path
        
        # 子ページを同期
        for block in blocks:
            if block["type"] == "child_page":
                child_dir = os.path.join(
                    self.config["markdown"][f"{db_name}Dir"],
                    block["child_page"]["title"]
                )
                os.makedirs(child_dir, exist_ok=True)
                await self.sync_page(block["id"], child_dir)

    async def sync_page(self, page_id: str, dir_path: str):
        """ページの同期"""
        page = self.notion.get_page(page_id)
        blocks = self.notion.get_page_blocks(page_id)
        
        markdown = BlockConverter.blocks_to_markdown(blocks)
        file_name = f"{page['properties']['title']['title'][0]['plain_text']}.md"
        file_path = os.path.join(dir_path, file_name)
        
        content = self.add_metadata(markdown, {
            "notionId": page_id,
            "lastSynced": "now",
        })
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.page_map[page_id] = file_path

    async def sync_from_markdown(self):
        """MarkdownからNotionへの同期"""
        try:
            for db_name in self.config["notion"]["databases"]:
                dir_path = self.config["markdown"][f"{db_name}Dir"]
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            await self.handle_markdown_change(file_path)
        except Exception as e:
            console.error("Markdownからの同期中にエラーが発生しました")
            console.error(e)
            raise

    async def handle_markdown_change(self, file_path: str):
        """Markdownファイルの変更を処理"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            metadata, markdown = self.parse_metadata(content)
            if "notionId" in metadata:
                blocks = self.markdown_to_blocks(markdown)
                self.notion.update_page(metadata["notionId"], blocks)
        except Exception as e:
            console.error(f"ファイルの変更処理中にエラーが発生しました: {file_path}")
            console.error(e)

    def start_watching(self):
        """ファイル変更の監視を開始"""
        if not self.config["sync"]["watchMode"]:
            return

        for db_name in self.config["notion"]["databases"]:
            dir_path = self.config["markdown"][f"{db_name}Dir"]
            self.observer.schedule(
                MarkdownHandler(self),
                dir_path,
                recursive=True
            )
        
        self.observer.start()
        console.print("[bold green]ファイル変更の監視を開始[/]")

    def stop(self):
        """監視を停止"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            console.print("[bold yellow]ファイル変更の監視を停止[/]")

    @staticmethod
    def add_metadata(content: str, metadata: Dict[str, Any]) -> str:
        """メタデータを追加"""
        metadata_str = "\n".join(
            f"{k}: {v}" for k, v in metadata.items()
        )
        return f"---\n{metadata_str}\n---\n\n{content}"

    @staticmethod
    def parse_metadata(content: str) -> tuple[Dict[str, Any], str]:
        """メタデータを解析"""
        if not content.startswith("---\n"):
            return {}, content

        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return {}, content

        metadata = {}
        for line in parts[1].strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        return metadata, parts[2]

    @staticmethod
    def markdown_to_blocks(markdown: str) -> List[Dict[str, Any]]:
        """MarkdownをNotionブロックに変換"""
        # この部分は必要に応じて実装
        return [] 