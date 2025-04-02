import { Client, GetPageResponse, BlockObjectResponse } from '@notionhq/client';
import TurndownService from 'turndown';

export class Page {
  private static turndown = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced',
  });

  static async toMarkdown(page: GetPageResponse, blocks: { results: BlockObjectResponse[] }): Promise<string> {
    let markdown = '';

    // タイトルを追加
    if ('properties' in page && 'title' in page.properties) {
      const title = page.properties.title.title[0]?.plain_text || 'Untitled';
      markdown += `# ${title}\n\n`;
    }

    // ブロックを変換
    for (const block of blocks.results) {
      markdown += this.blockToMarkdown(block);
    }

    return markdown;
  }

  static async toNotionBlocks(content: string): Promise<any[]> {
    // MarkdownからNotionブロックへの変換ロジック
    // この部分は必要に応じて実装
    return [];
  }

  private static blockToMarkdown(block: BlockObjectResponse): string {
    switch (block.type) {
      case 'paragraph':
        return `${block.paragraph.rich_text.map(text => text.plain_text).join('')}\n\n`;
      case 'heading_1':
        return `# ${block.heading_1.rich_text.map(text => text.plain_text).join('')}\n\n`;
      case 'heading_2':
        return `## ${block.heading_2.rich_text.map(text => text.plain_text).join('')}\n\n`;
      case 'heading_3':
        return `### ${block.heading_3.rich_text.map(text => text.plain_text).join('')}\n\n`;
      case 'bulleted_list_item':
        return `- ${block.bulleted_list_item.rich_text.map(text => text.plain_text).join('')}\n`;
      case 'numbered_list_item':
        return `1. ${block.numbered_list_item.rich_text.map(text => text.plain_text).join('')}\n`;
      case 'code':
        return `\`\`\`${block.code.language}\n${block.code.rich_text.map(text => text.plain_text).join('')}\n\`\`\`\n\n`;
      case 'image':
        return `![${block.image.caption.map(text => text.plain_text).join('')}](${block.image.file.url})\n\n`;
      default:
        return '';
    }
  }
} 