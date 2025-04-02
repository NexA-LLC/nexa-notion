from typing import List, Dict, Any, Optional
from notion_client import Client
from rich.console import Console

console = Console()

class NotionClient:
    def __init__(self, token: str):
        self.client = Client(auth=token)

    def get_page(self, page_id: str) -> Dict[str, Any]:
        """ページの情報を取得"""
        try:
            return self.client.pages.retrieve(page_id=page_id)
        except Exception as e:
            console.error(f"ページの取得に失敗しました: {page_id}")
            console.error(e)
            raise

    def get_page_blocks(self, page_id: str) -> List[Dict[str, Any]]:
        """ページのブロックを取得"""
        try:
            blocks = self.client.blocks.children.list(block_id=page_id)
            return blocks["results"]
        except Exception as e:
            console.error(f"ブロックの取得に失敗しました: {page_id}")
            console.error(e)
            raise

    def update_page(self, page_id: str, blocks: List[Dict[str, Any]]) -> None:
        """ページのブロックを更新"""
        try:
            # 既存のブロックを削除
            existing_blocks = self.get_page_blocks(page_id)
            for block in existing_blocks:
                self.client.blocks.delete(block_id=block["id"])

            # 新しいブロックを追加
            if blocks:
                self.client.blocks.children.append(
                    block_id=page_id,
                    children=blocks
                )
        except Exception as e:
            console.error(f"ページの更新に失敗しました: {page_id}")
            console.error(e)
            raise

    def get_database_pages(self, database_id: str) -> List[Dict[str, Any]]:
        """データベースのページを取得"""
        try:
            response = self.client.databases.query(database_id=database_id)
            return response["results"]
        except Exception as e:
            console.error(f"データベースの取得に失敗しました: {database_id}")
            console.error(e)
            raise

    def create_page(self, database_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """新しいページを作成"""
        try:
            return self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
        except Exception as e:
            console.error(f"ページの作成に失敗しました: {database_id}")
            console.error(e)
            raise

    def delete_page(self, page_id: str) -> None:
        """ページを削除（アーカイブ）"""
        try:
            self.client.pages.update(
                page_id=page_id,
                archived=True
            )
        except Exception as e:
            console.error(f"ページの削除に失敗しました: {page_id}")
            console.error(e)
            raise 