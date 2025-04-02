import * as dotenv from 'dotenv';
import { Config, DatabaseConfig } from '../types';

// .envファイルを読み込む
dotenv.config();

function loadDatabaseConfig(prefix: string): DatabaseConfig {
  const databaseId = process.env[`NOTION_${prefix.toUpperCase()}_DATABASE_ID`];
  const rootPageId = process.env[`NOTION_${prefix.toUpperCase()}_ROOT_PAGE_ID`];

  if (!databaseId || !rootPageId) {
    throw new Error(`必須の環境変数 NOTION_${prefix.toUpperCase()}_DATABASE_ID または NOTION_${prefix.toUpperCase()}_ROOT_PAGE_ID が設定されていません。`);
  }

  return {
    id: databaseId,
    rootPageId,
    excludedPages: [],
  };
}

export function loadConfig(): Config {
  // 必須の環境変数をチェック
  if (!process.env.NOTION_TOKEN) {
    throw new Error('必須の環境変数 NOTION_TOKEN が設定されていません。');
  }

  return {
    notion: {
      token: process.env.NOTION_TOKEN,
      databases: {
        spec: loadDatabaseConfig('spec'),
        docs: loadDatabaseConfig('docs'),
      },
    },
    markdown: {
      rootDir: process.env.MARKDOWN_ROOT_DIR || '../../specification',
      specDir: process.env.MARKDOWN_SPEC_DIR || '../../specification',
      docsDir: process.env.MARKDOWN_DOCS_DIR || '../../docs',
      excludedPatterns: [
        'node_modules/**',
        '.git/**',
        '**/*.test.md',
        '**/README.md',
      ],
    },
    sync: {
      watchMode: process.env.SYNC_WATCH_MODE === 'true',
      syncInterval: parseInt(process.env.SYNC_INTERVAL || '300000', 10),
      maxRetries: parseInt(process.env.SYNC_MAX_RETRIES || '3', 10),
      retryDelay: parseInt(process.env.SYNC_RETRY_DELAY || '1000', 10),
    },
  };
} 