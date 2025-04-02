import { MarkdownMetadata } from './parser';

export class MarkdownWriter {
  static addMetadata(content: string, metadata: MarkdownMetadata): string {
    const frontmatter = Object.entries(metadata)
      .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
      .join('\n');

    return `---\n${frontmatter}\n---\n\n${content}`;
  }

  static removeMetadata(content: string): string {
    const lines = content.split('\n');
    let startIndex = -1;
    let endIndex = -1;

    for (let i = 0; i < lines.length; i++) {
      if (lines[i].trim() === '---') {
        if (startIndex === -1) {
          startIndex = i;
        } else {
          endIndex = i;
          break;
        }
      }
    }

    if (startIndex === -1 || endIndex === -1) {
      return content;
    }

    return lines.slice(endIndex + 1).join('\n');
  }
} 