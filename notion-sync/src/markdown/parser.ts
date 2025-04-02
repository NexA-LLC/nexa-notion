import * as matter from 'gray-matter';
import { marked } from 'marked';

export interface MarkdownMetadata {
  notionId?: string;
  lastSynced?: string;
  [key: string]: any;
}

export interface ParsedMarkdown {
  data: MarkdownMetadata;
  content: string;
  html?: string;
}

export class MarkdownParser {
  static parse(content: string): ParsedMarkdown {
    const { data, content: markdown } = matter(content);
    const html = marked(markdown);

    return {
      data: data as MarkdownMetadata,
      content: markdown,
      html,
    };
  }

  static stringify(data: MarkdownMetadata, content: string): string {
    return matter.stringify(content, data);
  }
} 