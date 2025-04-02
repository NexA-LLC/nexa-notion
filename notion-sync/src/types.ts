export interface DatabaseConfig {
  id: string;
  rootPageId: string;
  excludedPages: string[];
}

export interface Config {
  notion: {
    token: string;
    databases: {
      spec: DatabaseConfig;
      docs: DatabaseConfig;
      [key: string]: DatabaseConfig; // 将来的な拡張用
    };
  };
  markdown: {
    rootDir: string;
    specDir: string;
    docsDir: string;
    excludedPatterns: string[];
  };
  sync: {
    watchMode: boolean;
    syncInterval: number;
    maxRetries: number;
    retryDelay: number;
  };
}

export interface NotionPage {
  id: string;
  title: string;
  content: string;
  children: NotionPage[];
  metadata: {
    notionId: string;
    lastSynced: string;
  };
}

export interface SyncResult {
  success: boolean;
  error?: string;
  pagesSynced: number;
  filesSynced: number;
} 