# Notion-Markdown 同期スクリプト

## 概要
NotionのチームスペースとMarkdownファイルの双方向同期を行うスクリプトです。

## 機能
- NotionからMarkdownへの同期
  - ページの内容を取得
  - ページの階層構造を維持
  - ページのUUIDを保持
- MarkdownからNotionへの同期
  - 変更されたMarkdownファイルの検知
  - Notionページの更新
- 階層構造の維持
  - フォルダ構造とNotionのページ階層を同期
  - ページの移動・名前変更に対応

## セットアップ
1. 依存パッケージのインストール
```bash
npm install
```

2. 環境変数の設定
```bash
# .env.exampleをコピーして.envを作成
cp .env.example .env

# .envファイルを編集して必要な値を設定
```

必須の環境変数：
- `NOTION_TOKEN`: Notionのインテグレーショントークン
- `NOTION_DATABASE_ID`: 同期対象のデータベースID
- `NOTION_ROOT_PAGE_ID`: 同期開始ページのID

オプションの環境変数：
- `SYNC_WATCH_MODE`: ファイル変更の監視モード（デフォルト: true）
- `SYNC_INTERVAL`: 同期間隔（ミリ秒、デフォルト: 300000）
- `SYNC_MAX_RETRIES`: 最大リトライ回数（デフォルト: 3）
- `SYNC_RETRY_DELAY`: リトライ間隔（ミリ秒、デフォルト: 1000）
- `MARKDOWN_ROOT_DIR`: Markdownファイルのルートディレクトリ
- `MARKDOWN_SPEC_DIR`: 仕様書のディレクトリ
- `MARKDOWN_DOCS_DIR`: ドキュメントのディレクトリ

## 使用方法
```bash
# 全ページの同期を実行
npm run sync

# 特定のページのみ同期
npm run sync -- --page-id <page_id>
```

## ファイル構成
```
scripts/notion-sync/
├── README.md
├── package.json
├── .env.example
├── .env
├── src/
│   ├── index.ts
│   ├── notion/
│   │   ├── client.ts
│   │   ├── page.ts
│   │   └── types.ts
│   ├── markdown/
│   │   ├── parser.ts
│   │   └── writer.ts
│   ├── sync/
│   │   ├── manager.ts
│   │   └── utils.ts
│   └── utils/
│       └── env.ts
└── tests/
    └── sync.test.ts
```

## 注意事項
- `.env`ファイルはGitにコミットしないでください
- 初回同期時は、既存のMarkdownファイルをバックアップすることをお勧めします
- Notionのインテグレーションに適切な権限を付与してください 