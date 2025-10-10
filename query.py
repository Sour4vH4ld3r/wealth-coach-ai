#!/usr/bin/env python3
"""
Wealth Coach AI Assistant - Interactive Query Tool

This script provides an interactive command-line interface to query
the Wealth Coach AI Assistant API.
"""

import sys
import json
import requests
from typing import Optional
import argparse
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "dev-key-12345"

# ANSI color codes
class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

def print_header():
    """Print application header"""
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}")
    print(f"{Colors.BLUE}{'Wealth Coach AI Assistant - Interactive Query Tool':^70}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*70}{Colors.NC}\n")

def check_server_health() -> bool:
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def send_query(message: str, user_id: Optional[str] = None) -> dict:
    """
    Send a query to the Wealth Coach API

    Args:
        message: The question to ask
        user_id: Optional user ID for conversation tracking

    Returns:
        API response as dictionary
    """
    url = f"{API_BASE_URL}/api/v1/chat/message"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    payload = {"message": message}
    if user_id:
        payload["user_id"] = user_id

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def format_response(response: dict) -> None:
    """Format and print the API response"""
    if "error" in response:
        print(f"{Colors.RED}✗ Error: {response.get('message', response['error'])}{Colors.NC}\n")
        return

    if "response" in response:
        print(f"{Colors.GREEN}Answer:{Colors.NC}")
        print(f"{response['response']}\n")

        # Show metadata if available
        if "metadata" in response:
            metadata = response["metadata"]
            print(f"{Colors.CYAN}Metadata:{Colors.NC}")
            if "sources_count" in metadata:
                print(f"  • Sources consulted: {metadata['sources_count']}")
            if "response_time" in metadata:
                print(f"  • Response time: {metadata['response_time']:.2f}s")
            if "model" in metadata:
                print(f"  • Model: {metadata['model']}")
            print()
    else:
        print(f"{Colors.YELLOW}Response:{Colors.NC}")
        print(json.dumps(response, indent=2))
        print()

def interactive_mode():
    """Run in interactive mode - continuous Q&A"""
    print_header()

    # Check server
    print(f"{Colors.YELLOW}Checking server connection...{Colors.NC}")
    if not check_server_health():
        print(f"{Colors.RED}✗ Server is not running!{Colors.NC}")
        print("Start the server with: ./start.sh")
        sys.exit(1)
    print(f"{Colors.GREEN}✓ Connected to server{Colors.NC}\n")

    print(f"{Colors.CYAN}Welcome to the Wealth Coach AI Assistant!{Colors.NC}")
    print("Ask me anything about personal finance, investing, budgeting, or retirement planning.")
    print(f"Type {Colors.BOLD}'exit'{Colors.NC} or {Colors.BOLD}'quit'{Colors.NC} to end the session.\n")

    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    query_count = 0

    while True:
        try:
            # Get user input
            question = input(f"{Colors.BOLD}You:{Colors.NC} ").strip()

            if not question:
                continue

            if question.lower() in ['exit', 'quit', 'q']:
                print(f"\n{Colors.CYAN}Thank you for using Wealth Coach AI! Goodbye!{Colors.NC}")
                break

            # Show processing indicator
            print(f"{Colors.YELLOW}Thinking...{Colors.NC}")

            # Send query
            response = send_query(question, user_id=session_id)
            query_count += 1

            # Format and display response
            print()
            format_response(response)
            print(f"{Colors.BLUE}{'-'*70}{Colors.NC}\n")

        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Session ended. Asked {query_count} questions.{Colors.NC}")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.NC}\n")

def single_query_mode(question: str):
    """Run a single query and exit"""
    # Check server
    if not check_server_health():
        print(f"{Colors.RED}✗ Server is not running!{Colors.NC}")
        print("Start the server with: ./start.sh")
        sys.exit(1)

    print(f"{Colors.CYAN}Question:{Colors.NC} {question}\n")

    # Send query
    response = send_query(question)

    # Format and display response
    format_response(response)

def main():
    """Main entry point"""
    global API_BASE_URL, API_KEY

    parser = argparse.ArgumentParser(
        description="Query the Wealth Coach AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python query.py

  # Single question
  python query.py "What is a 401k?"

  # Using short option
  python query.py -q "How much should I save for retirement?"

  # Check server health
  python query.py --health
        """
    )

    parser.add_argument(
        'question',
        nargs='?',
        help='Question to ask (if not provided, enters interactive mode)'
    )

    parser.add_argument(
        '-q', '--query',
        help='Question to ask (alternative to positional argument)'
    )

    parser.add_argument(
        '--health',
        action='store_true',
        help='Check server health and exit'
    )

    parser.add_argument(
        '--api-url',
        default=API_BASE_URL,
        help=f'API base URL (default: {API_BASE_URL})'
    )

    parser.add_argument(
        '--api-key',
        default=API_KEY,
        help='API key for authentication'
    )

    args = parser.parse_args()

    # Update global config
    API_BASE_URL = args.api_url
    API_KEY = args.api_key

    # Handle health check
    if args.health:
        print("Checking server health...")
        if check_server_health():
            print(f"{Colors.GREEN}✓ Server is healthy{Colors.NC}")
            try:
                response = requests.get(f"{API_BASE_URL}/api/v1/health/detailed")
                print(json.dumps(response.json(), indent=2))
            except:
                pass
            sys.exit(0)
        else:
            print(f"{Colors.RED}✗ Server is not responding{Colors.NC}")
            sys.exit(1)

    # Determine question source
    question = args.query or args.question

    if question:
        # Single query mode
        single_query_mode(question)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
