"""
Scanner module for Endpoint Interest Scorer.
Responsible for sending HTTP requests and collecting response data.
"""

import requests
from config import REQUEST_TIMEOUT, MAX_BODY_PREVIEW


def scan_url(url):
    """
    Send HTTP GET request to URL and collect response data.
    
    Args:
        url (str): URL to scan
        
    Returns:
        dict: Dictionary containing:
            - url: Original URL
            - status_code: HTTP status code (or None if error)
            - headers: Response headers dict
            - content_type: Content-Type header value
            - response_size: Size of response body in bytes
            - body_preview: Preview of response body (limited)
            - error: Error message if request failed
    """
    result = {
        'url': url,
        'status_code': None,
        'headers': {},
        'content_type': None,
        'response_size': 0,
        'body_preview': '',
        'error': None,
    }
    
    try:
        # Send GET request with timeout
        response = requests.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        
        # Collect status code
        result['status_code'] = response.status_code
        
        # Collect headers
        result['headers'] = dict(response.headers)
        
        # Extract Content-Type
        result['content_type'] = response.headers.get('Content-Type', '').split(';')[0].strip()
        
        # Get response size
        result['response_size'] = len(response.content)
        
        # Get body preview (limit size)
        try:
            # Try to decode as text
            body_text = response.text[:MAX_BODY_PREVIEW]
            result['body_preview'] = body_text
        except Exception:
            # If decoding fails, use empty string
            result['body_preview'] = ''
        
    except requests.exceptions.Timeout:
        result['error'] = f"Request timeout after {REQUEST_TIMEOUT} seconds"
    except requests.exceptions.ConnectionError:
        result['error'] = "Connection error - could not reach the server"
    except requests.exceptions.TooManyRedirects:
        result['error'] = "Too many redirects"
    except requests.exceptions.RequestException as e:
        result['error'] = f"Request error: {str(e)}"
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
    
    return result
