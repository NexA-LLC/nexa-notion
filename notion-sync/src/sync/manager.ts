import { Client } from '@notionhq/client';
import { Page } from '../notion/page';
import { MarkdownParser } from '../markdown/parser';
import { MarkdownWriter } from '../markdown/writer';
import { Config } from '../types';
import * as fs from 'fs';
import * as path from 'path';
import * as chokidar from 'chokidar';

export class SyncManager {
  private notion: Client;
  private config: Config;
  private pageMap: Map<string, string>; // UUID -> filePath
  private watcher: chokidar.FSWatcher;

  constructor(config: Config) {
    this.config = config;
    this.notion = new Client({
      auth: process.env.NOTION_TOKEN,
    });
    this.pageMap = new Map();
    this.watcher = chokidar.watch(config.markdown.rootDir, {
      ignored: config.markdown.excludedPatterns,
      persistent: config.sync.watchMode,
    });
  }

  async syncFromNotion() {
    try {
      const rootPage = await this.notion.pages.retrieve({
        page_id: this.config.notion.rootPageId,
      });

      await this.syncPage(rootPage.id, this.config.markdown.rootDir);
    } catch (error) {
      console.error('Notionからの同期中にエラーが発生しました:', error);
      throw error;
    }
  }

  async syncFromMarkdown() {
    try {
      const files = await this.getMarkdownFiles();
      for (const file of files) {
        const content = await fs.promises.readFile(file, 'utf-8');
        const { data, content: markdown } = MarkdownParser.parse(content);
        
        if (data.notionId) {
          await this.updateNotionPage(data.notionId, markdown);
        }
      }
    } catch (error) {
      console.error('Markdownからの同期中にエラーが発生しました:', error);
      throw error;
    }
  }

  private async syncPage(pageId: string, dirPath: string) {
    const page = await this.notion.pages.retrieve({ page_id: pageId });
    const blocks = await this.notion.blocks.children.list({ block_id: pageId });
    
    // ページの内容をMarkdownに変換
    const markdown = await Page.toMarkdown(page, blocks);
    
    // ファイルパスを生成
    const fileName = `${page.properties.title.title[0].plain_text}.md`;
    const filePath = path.join(dirPath, fileName);
    
    // メタデータを追加
    const content = MarkdownWriter.addMetadata(markdown, {
      notionId: pageId,
      lastSynced: new Date().toISOString(),
    });
    
    // ファイルを保存
    await fs.promises.writeFile(filePath, content);
    this.pageMap.set(pageId, filePath);
    
    // 子ページを同期
    for (const block of blocks.results) {
      if (block.type === 'child_page') {
        const childDir = path.join(dirPath, block.child_page.title);
        await fs.promises.mkdir(childDir, { recursive: true });
        await this.syncPage(block.id, childDir);
      }
    }
  }

  private async updateNotionPage(pageId: string, content: string) {
    const blocks = await Page.toNotionBlocks(content);
    await this.notion.blocks.children.append({
      block_id: pageId,
      children: blocks,
    });
  }

  private async getMarkdownFiles(): Promise<string[]> {
    const files: string[] = [];
    const dirs = [this.config.markdown.specDir, this.config.markdown.docsDir];
    
    for (const dir of dirs) {
      const entries = await fs.promises.readdir(dir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isFile() && entry.name.endsWith('.md')) {
          files.push(path.join(dir, entry.name));
        } else if (entry.isDirectory()) {
          const subFiles = await this.getMarkdownFiles();
          files.push(...subFiles);
        }
      }
    }
    
    return files;
  }

  startWatching() {
    if (!this.config.sync.watchMode) return;

    this.watcher
      .on('add', path => this.handleFileChange(path))
      .on('change', path => this.handleFileChange(path))
      .on('unlink', path => this.handleFileDelete(path));
  }

  private async handleFileChange(filePath: string) {
    if (!filePath.endsWith('.md')) return;
    
    try {
      const content = await fs.promises.readFile(filePath, 'utf-8');
      const { data } = MarkdownParser.parse(content);
      
      if (data.notionId) {
        await this.updateNotionPage(data.notionId, content);
      }
    } catch (error) {
      console.error(`ファイルの変更処理中にエラーが発生しました: ${filePath}`, error);
    }
  }

  private async handleFileDelete(filePath: string) {
    // ファイル削除時の処理（必要に応じて実装）
  }

  stop() {
    if (this.watcher) {
      this.watcher.close();
    }
  }
} 