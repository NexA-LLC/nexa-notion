import os
import asyncio
import click
from dotenv import load_dotenv
from rich.console import Console

from .types import Config
from .sync.manager import SyncManager

console = Console()

def load_config() -> Config:
    """設定を読み込む"""
    load_dotenv()
    
    return {
        "notion": {
            "token": os.getenv("NOTION_TOKEN", ""),
            "databases": {
                "management": {
                    "rootPageId": os.getenv("NOTION_MANAGEMENT_ROOT_PAGE_ID", ""),
                },
                "development": {
                    "rootPageId": os.getenv("NOTION_DEVELOPMENT_ROOT_PAGE_ID", ""),
                },
            }
        },
        "markdown": {
            "managementDir": os.getenv("MARKDOWN_MANAGEMENT_DIR", "management"),
            "developmentDir": os.getenv("MARKDOWN_DEVELOPMENT_DIR", "development"),
        },
        "sync": {
            "watchMode": os.getenv("SYNC_WATCH_MODE", "false").lower() == "true",
        }
    }

@click.group()
def cli():
    """NotionとMarkdownの同期ツール"""
    pass

@cli.command()
@click.option("--watch", is_flag=True, help="ファイル変更を監視")
def sync(watch: bool):
    """同期を実行"""
    config = load_config()
    if watch:
        config["sync"]["watchMode"] = True
    
    manager = SyncManager(config)
    
    try:
        asyncio.run(manager.sync_from_notion())
        asyncio.run(manager.sync_from_markdown())
        
        if watch:
            manager.start_watching()
            console.print("[bold green]同期が完了し、ファイル変更の監視を開始しました[/]")
            try:
                while True:
                    asyncio.sleep(1)
            except KeyboardInterrupt:
                manager.stop()
        else:
            console.print("[bold green]同期が完了しました[/]")
            
    except Exception as e:
        console.error("[bold red]同期中にエラーが発生しました[/]")
        console.error(e)
        raise click.Abort()

if __name__ == "__main__":
    cli() 