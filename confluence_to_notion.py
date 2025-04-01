#!/usr/bin/env python3
"""
Notion Confluence Space Bulk Importer

This script automates importing multiple Confluence spaces to Notion
by controlling the browser to perform the imports sequentially.
"""
import os
import sys
import time
import argparse
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv(dotenv_path=".env")

async def send_slack_notification(webhook_url, message):
    """Send notification to Slack using webhook URL"""
    if not webhook_url:
        return
        
    import requests
    try:
        response = requests.post(webhook_url, json={"text": message})
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending Slack notification: {str(e)}")
        return False

async def login_to_notion(page, email, password):
    """Login to Notion"""
    await page.goto('https://www.notion.so/login')
    await page.fill('input[name="email"]', email)
    await page.fill('input[name="password"]', password)
    await page.click('button[type="submit"]')
    
    # Wait for login to complete
    await page.wait_for_load_state('networkidle')
    
    # Check if login was successful
    if page.url.startswith('https://www.notion.so/login'):
        error_message = await page.inner_text('.notion-login-error')
        if error_message:
            raise Exception(f"Login failed: {error_message}")
        raise Exception("Login failed for unknown reasons")
    
    print("Successfully logged in to Notion")

async def import_confluence_space(page, confluence_url, space_key):
    """Import a single Confluence space to Notion"""
    # Navigate to Notion import page
    await page.goto('https://www.notion.so/import')
    
    # Click on Confluence import option
    await page.click('text=Confluence')
    
    # Wait for the Confluence import form to appear
    await page.wait_for_selector('input[placeholder="https://company.atlassian.net"]')
    
    # Fill in Confluence URL
    await page.fill('input[placeholder="https://company.atlassian.net"]', confluence_url)
    
    # Click Continue button
    await page.click('button:has-text("Continue")')
    
    # Wait for space selection page
    await page.wait_for_selector('input[placeholder="Search for a space"]')
    
    # Search for the specific space
    await page.fill('input[placeholder="Search for a space"]', space_key)
    await page.wait_for_timeout(1000)  # Wait for search results
    
    # Select the space (first result)
    await page.click('text=' + space_key)
    
    # Click Import button
    import_button = await page.wait_for_selector('button:has-text("Import")')
    await import_button.click()
    
    # Wait for import to start
    await page.wait_for_selector('text=Importing')
    
    # Wait for import to complete (this might take a while)
    # We'll look for a success message or completion indicator
    try:
        await page.wait_for_selector('text=Import complete', timeout=600000)  # 10 minute timeout
        print(f"Successfully imported Confluence space: {space_key}")
        return True
    except Exception as e:
        print(f"Import may still be in progress for space {space_key}: {str(e)}")
        return False

def read_spaces_from_file(file_path):
    """Read space keys from a file, one per line"""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading spaces file: {str(e)}")
        return []

async def main():
    """Main function to run the Confluence to Notion importer"""
    parser = argparse.ArgumentParser(description='Import multiple Confluence spaces to Notion')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--spaces', help='Comma-separated list of Confluence space keys to import')
    group.add_argument('--spaces-file', help='Path to file containing space keys, one per line')
    parser.add_argument('--confluence-url', help='Confluence URL (overrides environment variable)')
    parser.add_argument('--notion-email', help='Notion email (overrides environment variable)')
    parser.add_argument('--notion-password', help='Notion password (overrides environment variable)')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--limit', type=int, help='Limit the number of spaces to import')
    args = parser.parse_args()
    
    # Get credentials from environment variables or command line arguments
    notion_email = args.notion_email or os.getenv('NOTION_EMAIL')
    notion_password = args.notion_password or os.getenv('NOTION_PASSWORD')
    confluence_url = args.confluence_url or os.getenv('CONFLUENCE_URL')
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not notion_email or not notion_password:
        print("Error: Notion credentials not provided. Set NOTION_EMAIL and NOTION_PASSWORD "
              "environment variables or provide --notion-email and --notion-password arguments.")
        return 1
        
    if not confluence_url:
        print("Error: Confluence URL not provided. Set CONFLUENCE_URL environment variable "
              "or provide --confluence-url argument.")
        return 1
    
    # Get space keys from command line or file
    if args.spaces:
        space_keys = [space.strip() for space in args.spaces.split(',')]
    else:
        space_keys = read_spaces_from_file(args.spaces_file)
    
    if not space_keys:
        print("Error: No Confluence space keys provided")
        return 1
    
    # Apply limit if specified
    if args.limit and args.limit > 0:
        space_keys = space_keys[:args.limit]
        print(f"Limiting import to {args.limit} spaces")
    
    # Send start notification
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_message = (f"*Starting Confluence to Notion Import* ({current_time})\n"
                     f"Confluence URL: {confluence_url}\n"
                     f"Spaces to import: {', '.join(space_keys)}")
    await send_slack_notification(slack_webhook_url, start_message)
    
    # Start browser automation
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=args.headless)
        page = await browser.new_page()
        
        try:
            # Login to Notion
            await login_to_notion(page, notion_email, notion_password)
            
            # Import each space
            results = []
            for space_key in space_keys:
                print(f"Importing Confluence space: {space_key}")
                success = await import_confluence_space(page, confluence_url, space_key)
                results.append((space_key, success))
                
                # Small delay between imports
                await page.wait_for_timeout(5000)
            
            # Send completion notification
            completion_message = f"*Confluence to Notion Import Results* ({current_time})\n"
            for space_key, success in results:
                status = "✅ Complete" if success else "⚠️ In Progress/Failed"
                completion_message += f"• {space_key}: {status}\n"
            
            await send_slack_notification(slack_webhook_url, completion_message)
            
        except Exception as e:
            error_message = f"Error occurred during Confluence to Notion import: {str(e)}"
            print(error_message)
            await send_slack_notification(slack_webhook_url, f"⚠️ {error_message}")
        finally:
            await browser.close()
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())
