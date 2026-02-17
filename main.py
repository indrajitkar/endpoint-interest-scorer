"""
Main entry point for Endpoint Interest Scorer.
A CLI tool that scans URLs, detects APIs, and scores their interest level.
"""

import sys
import argparse
from scanner import scan_url
from detector import detect_api
from scorer import score_endpoint
from utils import is_valid_url, format_output, save_to_csv

# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    # Reset
    RESET = '\033[0m'
    
    # Text colors
    BOLD = '\033[1m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    DIM = '\033[2m'
    
    # Combined styles
    BOLD_CYAN = f'{BOLD}{CYAN}'
    BOLD_GREEN = f'{BOLD}{GREEN}'
    BOLD_YELLOW = f'{BOLD}{YELLOW}'
    BOLD_RED = f'{BOLD}{RED}'
    
    @staticmethod
    def disable():
        """Disable colors (for non-terminal output)."""
        Colors.RESET = ''
        Colors.BOLD = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.DIM = ''
        Colors.BOLD_CYAN = ''
        Colors.BOLD_GREEN = ''
        Colors.BOLD_YELLOW = ''
        Colors.BOLD_RED = ''

# Check if output is a terminal (Windows compatibility)
def is_terminal():
    """Check if stdout is a terminal."""
    try:
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    except:
        return False

# Disable colors if not a terminal
if not is_terminal():
    Colors.disable()


def load_urls(filename):
    """
    Load URLs from a text file.
    One URL per line.
    
    Args:
        filename (str): Path to input file
        
    Returns:
        list: List of URL strings
    """
    urls = []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                # Skip empty lines and comments
                if url and not url.startswith('#'):
                    # Validate URL
                    if is_valid_url(url):
                        urls.append(url)
                    else:
                        print(f"{Colors.YELLOW}Warning: Invalid URL skipped: {url}{Colors.RESET}", file=sys.stderr)
    except FileNotFoundError:
        print(f"{Colors.RED}Error: File '{filename}' not found.{Colors.RESET}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error reading file: {str(e)}{Colors.RESET}", file=sys.stderr)
        sys.exit(1)
    
    return urls


def main():
    """
    Main function - entry point of the program.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description=f'{Colors.BOLD_CYAN}Endpoint Interest Scorer{Colors.RESET} - Scan URLs and score API endpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CYAN}Example usage:{Colors.RESET}
  python main.py -s urls.txt
  python main.py --scan urls.txt -o results.csv
  python main.py -s urls.txt --output results.csv
        """
    )
    
    # Add custom help option --hh (in addition to default -h/--help)
    parser.add_argument(
        '--hh',
        action='help',
        help='Show this help message and exit (alias for --help)'
    )
    
    parser.add_argument(
        '-s', '--scan',
        required=True,
        metavar='FILE',
        help='Text file containing URLs to scan (one per line)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='results.csv',
        metavar='FILE',
        help='Output CSV filename (default: results.csv)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load URLs from file
    print(f"{Colors.CYAN}Loading URLs from {Colors.BOLD}{args.scan}{Colors.RESET}{Colors.CYAN}...{Colors.RESET}")
    urls = load_urls(args.scan)
    
    if not urls:
        print(f"{Colors.RED}No valid URLs found in input file.{Colors.RESET}", file=sys.stderr)
        sys.exit(1)
    
    print(f"{Colors.GREEN}Found {Colors.BOLD}{len(urls)}{Colors.RESET}{Colors.GREEN} valid URL(s). Starting scan...{Colors.RESET}\n")
    
    # Process each URL
    results = []
    
    for idx, url in enumerate(urls, 1):
        print(f"{Colors.CYAN}[{idx}/{len(urls)}]{Colors.RESET} {Colors.BOLD}Scanning:{Colors.RESET} {Colors.BLUE}{url}{Colors.RESET}")
        
        # Step 1: Scan URL
        scan_result = scan_url(url)
        
        if scan_result.get('error'):
            print(f"  {Colors.RED}✗ Error: {scan_result['error']}{Colors.RESET}")
            # Still add to results with error info
            results.append({
                'url': url,
                'status_code': None,
                'content_type': None,
                'response_size': 0,
                'is_api': False,
                'score': 0,
                'risk_level': 'Low',
                'matched_keywords': [],
                'api_indicators': [],
                'body_preview': scan_result.get('error', ''),
            })
            continue
        
        # Step 2: Detect if API
        detection_result = detect_api(
            url=url,
            content_type=scan_result.get('content_type', ''),
            body_preview=scan_result.get('body_preview', '')
        )
        
        # Step 3: Score if API
        scoring_result = score_endpoint(scan_result, detection_result['is_api'])
        
        # Combine all results
        result = {
            'url': url,
            'status_code': scan_result.get('status_code'),
            'content_type': scan_result.get('content_type', ''),
            'response_size': scan_result.get('response_size', 0),
            'is_api': detection_result['is_api'],
            'score': scoring_result['score'],
            'risk_level': scoring_result['risk_level'],
            'matched_keywords': scoring_result['matched_keywords'],
            'api_indicators': detection_result['indicators'],
            'body_preview': scan_result.get('body_preview', ''),
        }
        
        results.append(result)
        
        # Print quick status
        if detection_result['is_api']:
            print(f"  {Colors.GREEN}✓ API detected{Colors.RESET} | {Colors.BOLD}Score:{Colors.RESET} {Colors.YELLOW}{scoring_result['score']}{Colors.RESET} | {Colors.BOLD}Risk:{Colors.RESET} {Colors.MAGENTA}{scoring_result['risk_level']}{Colors.RESET}")
        else:
            print(f"  {Colors.DIM}- Not an API endpoint{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD_GREEN}Processing complete. Sorting results...{Colors.RESET}")
    
    # Sort results by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Print formatted output
    output_text = format_output(results)
    print(output_text)
    
    # Save to CSV
    try:
        csv_filename = save_to_csv(results, args.output)
        print(f"{Colors.GREEN}✓ Results saved to:{Colors.RESET} {Colors.BOLD_CYAN}{csv_filename}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}✗ Error saving CSV: {str(e)}{Colors.RESET}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
