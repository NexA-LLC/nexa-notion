import { Client } from '@notionhq/client';
import { DatabaseConfig } from '../types';

export class NotionClient {
  private client: Client;

  constructor(token: string) {
    this.client = new Client({
      auth: token,
    });
  }

  async getPage(pageId: string) {
    try {
      return await this.client.pages.retrieve({
        page_id: pageId,
      });
    } catch (error) {
      console.error(`ページの取得に失敗しました: ${pageId}`, error);
      throw error;
    }
  }

  async getPageBlocks(pageId: string) {
    try {
      const blocks = await this.client.blocks.children.list({
        block_id: pageId,
      });
      return blocks.results;
    } catch (error) {
      console.error(`ブロックの取得に失敗しました: ${pageId}`, error);
      throw error;
    }
  }

  async updatePage(pageId: string, blocks: any[]) {
    try {
      // 既存のブロックを削除
      const existingBlocks = await this.getPageBlocks(pageId);
      for (const block of existingBlocks) {
        await this.client.blocks.delete({
          block_id: block.id,
        });
      }

      // 新しいブロックを追加
      if (blocks.length > 0) {
        await this.client.blocks.children.append({
          block_id: pageId,
          children: blocks,
        });
      }
    } catch (error) {
      console.error(`ページの更新に失敗しました: ${pageId}`, error);
      throw error;
    }
  }

  async getDatabasePages(databaseId: string) {
    try {
      const response = await this.client.databases.query({
        database_id: databaseId,
      });
      return response.results;
    } catch (error) {
      console.error(`データベースの取得に失敗しました: ${databaseId}`, error);
      throw error;
    }
  }

  async createPage(databaseId: string, properties: any) {
    try {
      return await this.client.pages.create({
        parent: { database_id: databaseId },
        properties,
      });
    } catch (error) {
      console.error(`ページの作成に失敗しました: ${databaseId}`, error);
      throw error;
    }
  }

  async deletePage(pageId: string) {
    try {
      await this.client.pages.update({
        page_id: pageId,
        archived: true,
      });
    } catch (error) {
      console.error(`ページの削除に失敗しました: ${pageId}`, error);
      throw error;
    }
  }
} 