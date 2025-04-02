import os
import requests
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 定数
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
ORGANIZATION = os.getenv('GITHUB_ORGANIZATION', 'NexA-LLC')
REPO = os.getenv('GITHUB_REPO', 'antracing')
PROJECT_NUMBER = 6

# APIヘッダー
GITHUB_HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

NOTION_HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

def get_github_issues() -> List[Dict[str, Any]]:
    """GitHubのプロジェクトからIssueを取得"""
    query = """
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
    """
    
    variables = {
        'org': ORGANIZATION,
        'number': PROJECT_NUMBER
    }
    
    response = requests.post(
        'https://api.github.com/graphql',
        json={'query': query, 'variables': variables},
        headers=GITHUB_HEADERS
    )
    
    if response.status_code != 200:
        raise Exception(f'GitHub API error: {response.text}')
    
    data = response.json()
    issues = []
    
    for node in data['data']['organization']['projectV2']['items']['nodes']:
        if node['content']:
            issue = node['content']
            issues.append({
                'number': issue['number'],
                'title': issue['title'],
                'state': issue['state'],
                'labels': [label['name'] for label in issue['labels']['nodes']]
            })
    
    return issues

def get_existing_page(notion_client: requests.Session, title: str) -> str:
    """Notionデータベースから既存のページを検索"""
    query = {
        'filter': {
            'property': 'Name',
            'title': {
                'equals': title
            }
        }
    }
    
    response = notion_client.post(
        f'https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query',
        json=query,
        headers=NOTION_HEADERS
    )
    
    if response.status_code != 200:
        raise Exception(f'Notion API error: {response.text}')
    
    results = response.json()['results']
    return results[0]['id'] if results else None

def sync_issue_to_notion(notion_client: requests.Session, issue: Dict[str, Any]) -> None:
    """IssueをNotionに同期"""
    number = issue['number']
    title = issue['title']
    state = issue['state']
    labels = issue['labels']
    issue_url = f'https://github.com/{ORGANIZATION}/{REPO}/issues/{number}'
    
    properties = {
        'Name': {
            'title': [
                {
                    'text': {
                        'content': title
                    }
                }
            ]
        },
        'Status': {
            'status': {
                'name': '未着手' if state == 'OPEN' else '完了'
            }
        },
        'Labels': {
            'multi_select': [
                {'name': label} for label in labels
            ]
        },
        'URL': {
            'url': issue_url
        }
    }
    
    existing_page_id = get_existing_page(notion_client, title)
    
    if existing_page_id:
        # 既存ページの更新
        response = notion_client.patch(
            f'https://api.notion.com/v1/pages/{existing_page_id}',
            json={'properties': properties},
            headers=NOTION_HEADERS
        )
        print(f'更新: Issue #{number}')
    else:
        # 新規ページの作成
        response = notion_client.post(
            'https://api.notion.com/v1/pages',
            json={
                'parent': {'database_id': NOTION_DATABASE_ID},
                'properties': properties
            },
            headers=NOTION_HEADERS
        )
        print(f'作成: Issue #{number}')
    
    if response.status_code != 200:
        raise Exception(f'Notion API error: {response.text}')

def main():
    """メイン処理"""
    if not all([GITHUB_TOKEN, NOTION_TOKEN, NOTION_DATABASE_ID]):
        raise ValueError('必要な環境変数が設定されていません')
    
    try:
        # GitHubからIssueを取得
        issues = get_github_issues()
        
        # Notionクライアントの作成
        notion_client = requests.Session()
        
        # 各Issueを同期
        for issue in issues:
            sync_issue_to_notion(notion_client, issue)
            
    except Exception as e:
        print(f'エラー: {str(e)}')
        exit(1)

if __name__ == '__main__':
    main() 