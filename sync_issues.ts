import { Octokit } from '@octokit/rest';
import * as fs from 'fs';
import * as path from 'path';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const ORGANIZATION = 'NexA-LLC';
const PROJECT_NUMBER = 6;
const REPO = 'antracing';

if (!GITHUB_TOKEN) {
  console.error('GITHUB_TOKENが設定されていません');
  process.exit(1);
}

const octokit = new Octokit({
  auth: GITHUB_TOKEN
});

async function getProjectItems() {
  try {
    // GraphQL クエリでプロジェクトのアイテムを取得
    const query = `
      query($org: String!, $number: Int!) {
        organization(login: $org) {
          projectV2(number: $number) {
            items(first: 100) {
              nodes {
                content {
                  ... on Issue {
                    number
                    title
                    body
                    state
                    createdAt
                    updatedAt
                    labels(first: 10) {
                      nodes {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    `;

    const result = await octokit.graphql(query, {
      org: ORGANIZATION,
      number: PROJECT_NUMBER
    });

    return result.organization.projectV2.items.nodes;
  } catch (error) {
    console.error('プロジェクトアイテムの取得に失敗:', error);
    return [];
  }
}

async function saveIssuesToFiles() {
  const items = await getProjectItems();
  const issuesDir = path.join(process.cwd(), 'issues');

  // issuesディレクトリが存在しない場合は作成
  if (!fs.existsSync(issuesDir)) {
    fs.mkdirSync(issuesDir, { recursive: true });
  }

  for (const item of items) {
    if (!item.content) continue;

    const issue = item.content;
    const fileName = `${issue.number}-${issue.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.md`;
    const filePath = path.join(issuesDir, fileName);

    const content = `# ${issue.title}

## 概要
- Issue番号: #${issue.number}
- 状態: ${issue.state}
- 作成日: ${new Date(issue.createdAt).toLocaleDateString('ja-JP')}
- 更新日: ${new Date(issue.updatedAt).toLocaleDateString('ja-JP')}
${issue.labels.nodes.length > 0 ? `- ラベル: ${issue.labels.nodes.map(l => l.name).join(', ')}` : ''}

## 内容
${issue.body || '(内容なし)'}
`;

    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`保存完了: ${fileName}`);
  }
}

// スクリプト実行
saveIssuesToFiles().catch(console.error); 