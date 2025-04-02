import { Client } from '@notionhq/client';
import { PageObjectResponse, PartialPageObjectResponse, PartialDatabaseObjectResponse, DatabaseObjectResponse } from '@notionhq/client/build/src/api-endpoints';
import { Octokit } from '@octokit/rest';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const NOTION_TOKEN = process.env.NOTION_TOKEN;
const NOTION_DATABASE_ID = process.env.NOTION_DATABASE_ID;
const ORGANIZATION = process.env.GITHUB_ORGANIZATION || 'NexA-LLC';
const REPO = process.env.GITHUB_REPO || 'antracing';
const PROJECT_NUMBER = 6;
const NOTION_API_VERSION = '2022-06-28';

interface IssueContent {
  number: number;
  title: string;
  state: string;
  labels: {
    nodes: {
      name: string;
    }[];
  };
}

interface ProjectItem {
  content?: {
    number: number;
    title: string;
    state: string;
    labels: {
      nodes: { name: string }[];
    };
  };
}

interface QueryResult {
  organization: {
    projectV2: {
      items: {
        nodes: ProjectItem[];
      };
    };
  };
}

interface Issue {
  number: number;
  title: string;
  state: string;
  labels: string[];
}

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
});

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
                state
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

async function getGitHubIssues(): Promise<Issue[]> {
  try {
    const response = await octokit.graphql<any>(query, {
      org: ORGANIZATION,
      number: PROJECT_NUMBER,
    });

    if (!response.organization?.projectV2?.items?.nodes) {
      throw new Error("プロジェクトデータの取得に失敗しました");
    }

    return response.organization.projectV2.items.nodes
      .filter((node: any) => node.content)
      .map((node: any) => ({
        number: node.content.number,
        title: node.content.title,
        state: node.content.state,
        labels: node.content.labels.nodes.map((label: any) => label.name),
      }));
  } catch (error: any) {
    if (error.message.includes('API rate limit exceeded')) {
      const resetTime = new Date(parseInt(error.headers['x-ratelimit-reset']) * 1000);
      const waitTime = resetTime.getTime() - Date.now();
      console.error(`レート制限に達しました。リセット時間: ${resetTime.toLocaleString()}`);
      
      if (process.env.WAIT_FOR_RESET === 'true') {
        console.log(`${Math.ceil(waitTime / 1000)}秒待機します...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
        return getGitHubIssues();
      }
    }
    throw error;
  }
}

async function syncIssueToNotion(notionClient: Client, item: Issue) {
  try {
    const { number, title, state, labels } = item;
    const issueUrl = `https://github.com/${ORGANIZATION}/${REPO}/issues/${number}`;

    const existingEntries = await notionClient.databases.query({
      database_id: NOTION_DATABASE_ID || '',
      filter: {
        property: 'Name',
        title: {
          equals: title
        }
      }
    });

    const existingEntry = existingEntries.results[0] as PageObjectResponse | undefined;

    const properties = {
      'Name': {
        title: [
          {
            text: {
              content: title
            }
          }
        ]
      },
      'Status': {
        status: {
          name: state === 'OPEN' ? '未着手' : '完了'
        }
      },
      'Labels': {
        multi_select: labels.map(label => ({
          name: label
        }))
      },
      'URL': {
        url: issueUrl
      }
    };

    if (existingEntry) {
      await notionClient.pages.update({
        page_id: existingEntry.id,
        properties
      });
      console.log(`更新: Issue #${number}`);
    } else {
      await notionClient.pages.create({
        parent: {
          database_id: NOTION_DATABASE_ID || ''
        },
        properties
      });
      console.log(`作成: Issue #${number}`);
    }
  } catch (error) {
    console.error('エラー:', error);
  }
}

async function syncToNotion(issues: ProjectItem[]) {
  if (!NOTION_TOKEN || !NOTION_DATABASE_ID) {
    throw new Error('NOTION_TOKEN と NOTION_DATABASE_ID が必要です');
  }

  const notion = new Client({
    auth: NOTION_TOKEN
  });

  for (const item of issues) {
    if (!item.content) continue;

    const issueData: Issue = {
      number: item.content.number,
      title: item.content.title,
      state: item.content.state,
      labels: item.content.labels.nodes.map(node => node.name)
    };

    await syncIssueToNotion(notion, issueData);
  }
}

async function main() {
  try {
    const issues = await getGitHubIssues();
    const notion = new Client({
      auth: NOTION_TOKEN
    });

    for (const issue of issues) {
      await syncIssueToNotion(notion, issue);
    }
  } catch (error) {
    console.error('エラー:', error);
    process.exit(1);
  }
}

main(); 