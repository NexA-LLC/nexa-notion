#!/usr/bin/env python3
"""
Confluence Space List Generator

This script retrieves a list of all spaces from a Confluence instance
and outputs their keys to a file or stdout.
"""
import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env")

def get_confluence_spaces(confluence_url, api_token):
    """Retrieve all spaces from Confluence using the API"""
    import requests
    from requests.auth import HTTPBasicAuth
    
    # Prepare API endpoint URL
    if confluence_url.endswith('/'):
        api_url = f"{confluence_url}rest/api/space"
    else:
        api_url = f"{confluence_url}/rest/api/space"
    
    # Set up parameters for pagination
    params = {
        'limit': 100,
        'start': 0,
        'status': 'current'
    }
    
    # Set up authentication
    auth = HTTPBasicAuth('', api_token)  # Username is ignored when using API token
    
    # Initialize results
    all_spaces = []
    
    # Fetch all spaces with pagination
    while True:
        try:
            response = requests.get(api_url, params=params, auth=auth)
            response.raise_for_status()
            
            data = response.json()
            spaces = data.get('results', [])
            
            if not spaces:
                break
                
            all_spaces.extend(spaces)
            
            # Check if there are more spaces to fetch
            if len(spaces) < params['limit']:
                break
                
            # Update start parameter for next page
            params['start'] += params['limit']
            
        except Exception as e:
            print(f"Error retrieving Confluence spaces: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    return all_spaces

def main():
    """Main function to run the Confluence space list generator"""
    parser = argparse.ArgumentParser(description='List all spaces from a Confluence instance')
    parser.add_argument('--confluence-url', help='Confluence URL (overrides environment variable)')
    parser.add_argument('--api-token', help='Confluence API token (overrides environment variable)')
    parser.add_argument('--output', help='Output file path (default: stdout)')
    parser.add_argument('--format', choices=['keys', 'full'], default='keys',
                        help='Output format: keys (default) or full JSON')
    args = parser.parse_args()
    
    # Get credentials from environment variables or command line arguments
    confluence_url = args.confluence_url or os.getenv('CONFLUENCE_URL')
    api_token = args.api_token or os.getenv('CONFLUENCE_API_TOKEN')
    
    if not confluence_url:
        print("Error: Confluence URL not provided. Set CONFLUENCE_URL environment variable "
              "or provide --confluence-url argument.", file=sys.stderr)
        return 1
        
    if not api_token:
        print("Error: Confluence API token not provided. Set CONFLUENCE_API_TOKEN environment variable "
              "or provide --api-token argument.", file=sys.stderr)
        return 1
    
    # Get spaces from Confluence
    spaces = get_confluence_spaces(confluence_url, api_token)
    
    # Prepare output
    if args.format == 'keys':
        output = '\n'.join([space['key'] for space in spaces])
    else:
        import json
        output = json.dumps(spaces, indent=2)
    
    # Write output to file or stdout
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Wrote {len(spaces)} spaces to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing to output file: {str(e)}", file=sys.stderr)
            return 1
    else:
        print(output)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
