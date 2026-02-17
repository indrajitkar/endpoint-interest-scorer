"""
Utility functions for Endpoint Interest Scorer.
Contains helper functions for URL validation, keyword checking, formatting, and file operations.
"""

import sys
import csv
from urllib.parse import urlparse
from config import KEYWORDS


def is_terminal():
    """Check if stdout is a terminal."""
    try:
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    except:
        return False


def is_valid_url(url):
    """
    Validate if a string is a valid URL.
    
    Args:
        url (str): URL string to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    try:
        result = urlparse(url.strip())
        # Check if URL has both scheme and netloc
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def check_keywords(text):
    """
    Check if text contains any keywords from the keyword list.
    Case-insensitive search.
    
    Args:
        text (str): Text to search in
        
    Returns:
        list: List of matched keywords
    """
    if not text:
        return []
    
    text_lower = text.lower()
    matched = []
    
    for keyword in KEYWORDS:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    
    return matched


def has_url_parameters(url):
    """
    Check if URL contains query parameters.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if URL has parameters, False otherwise
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.query)
    except Exception:
        return False


def format_output(results):
    """
    Format results for terminal display.
    
    Args:
        results (list): List of result dictionaries
        
    Returns:
        str: Formatted string for display
    """
    # ANSI color codes (only if terminal supports it)
    if is_terminal():
        BOLD_CYAN = '\033[1m\033[36m'
        RESET = '\033[0m'
    else:
        BOLD_CYAN = ''
        RESET = ''
    
    if not results:
        return "No results to display.\n"
    
    output = []
    output.append("\n" + "="*100)
    output.append(f"{BOLD_CYAN}ENDPOINT INTEREST SCORER - RESULTS{RESET}")
    output.append("="*100 + "\n")
    
    for idx, result in enumerate(results, 1):
        output.append(f"{idx}. {result['url']}")
        output.append(f"   Status: {result['status_code']} | "
                     f"Content-Type: {result['content_type']} | "
                     f"Size: {result['response_size']} bytes")
        output.append(f"   Is API: {result['is_api']} | "
                     f"Score: {result['score']} | "
                     f"Risk Level: {result['risk_level']}")
        
        if result['matched_keywords']:
            output.append(f"   Keywords: {', '.join(result['matched_keywords'])}")
        
        if result['api_indicators']:
            output.append(f"   API Indicators: {', '.join(result['api_indicators'])}")
        
        if result['body_preview']:
            preview = result['body_preview'].replace('\n', ' ')[:100]
            output.append(f"   Preview: {preview}...")
        
        output.append("")
    
    output.append("="*100 + "\n")
    
    return "\n".join(output)


def save_to_csv(results, filename='results.csv'):
    """
    Save results to a CSV file.
    
    Args:
        results (list): List of result dictionaries
        filename (str): Output CSV filename
        
    Returns:
        str: Path to saved file
    """
    if not results:
        return None
    
    # Define CSV columns
    fieldnames = [
        'url',
        'status_code',
        'content_type',
        'response_size',
        'is_api',
        'score',
        'risk_level',
        'matched_keywords',
        'api_indicators',
        'body_preview',
    ]
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # Convert lists to strings for CSV
                row = result.copy()
                row['matched_keywords'] = ', '.join(result.get('matched_keywords', []))
                row['api_indicators'] = ', '.join(result.get('api_indicators', []))
                writer.writerow(row)
        
        return filename
    except Exception as e:
        raise Exception(f"Error saving CSV file: {str(e)}")
