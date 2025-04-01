# Tool Notion

ConfluenceからNotionへの移行を支援するツールです。

## 機能

- Confluenceのスペース一覧の取得
- ConfluenceのページをNotionのページに変換して移行
- ページの階層構造の保持
- 添付ファイルの移行

## セットアップ

1. 必要なパッケージのインストール:
```bash
pip install -r requirements.txt
```

2. 環境変数の設定:
```bash
cp .env.confluence_notion.example .env
```
`.env`ファイルを編集し、必要な認証情報を設定してください。

## 使用方法

### Confluenceのスペース一覧を取得
```bash
python list_confluence_spaces.py
```

### ConfluenceからNotionへの移行
```bash
python confluence_to_notion.py
```

## 環境変数

- `CONFLUENCE_URL`: ConfluenceのURL
- `CONFLUENCE_USERNAME`: Confluenceのユーザー名
- `CONFLUENCE_API_TOKEN`: ConfluenceのAPIトークン
- `NOTION_TOKEN`: NotionのAPIトークン
- `NOTION_DATABASE_ID`: 移行先のNotionデータベースID

## 注意事項

- ConfluenceのAPIトークンは、Confluenceの設定から生成できます
- NotionのAPIトークンは、Notionの設定から生成できます
- データベースIDは、NotionのデータベースURLから取得できます 