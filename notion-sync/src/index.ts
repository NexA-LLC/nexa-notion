import { Command } from 'commander';
import { SyncManager } from './sync/manager';
import { loadConfig } from './utils/env';

const program = new Command();

program
  .name('notion-sync')
  .description('NotionとMarkdownの双方向同期スクリプト')
  .version('1.0.0');

program
  .command('sync')
  .description('同期を実行')
  .option('-p, --page-id <pageId>', '特定のページのみ同期')
  .action(async (options) => {
    try {
      const config = loadConfig();
      const manager = new SyncManager(config);

      if (options.pageId) {
        // 特定のページのみ同期
        await manager.syncPage(options.pageId, config.markdown.rootDir);
      } else {
        // 全ページを同期
        await manager.syncFromNotion();
        await manager.syncFromMarkdown();
        manager.startWatching();
      }
    } catch (error) {
      console.error('同期中にエラーが発生しました:', error);
      process.exit(1);
    }
  });

program.parse(); 