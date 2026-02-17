"""
Detector module for Endpoint Interest Scorer.
Responsible for detecting if a URL is an API endpoint.
"""

import json
from config import API_PATTERNS


def detect_api(url, content_type, body_preview):
    """
    Detect if URL is an API endpoint based on various indicators.
    
    Args:
        url (str): URL to check
        content_type (str): Content-Type header value
        body_preview (str): Preview of response body
        
    Returns:
        dict: Dictionary containing:
            - is_api: Boolean indicating if URL is an API
            - indicators: List of matched indicators
    """
    result = {
        'is_api': False,
        'indicators': [],
    }
    
    # Check URL patterns
    url_lower = url.lower()
    for pattern in API_PATTERNS:
        if pattern.lower() in url_lower:
            result['is_api'] = True
            result['indicators'].append(f"URL pattern: {pattern}")
    
    # Check Content-Type for JSON
    if content_type and 'application/json' in content_type.lower():
        result['is_api'] = True
        result['indicators'].append("Content-Type: application/json")
    
    # Check if response body is valid JSON
    if body_preview:
        try:
            # Try to parse as JSON
            json.loads(body_preview)
            result['is_api'] = True
            result['indicators'].append("Valid JSON response")
        except (json.JSONDecodeError, ValueError):
            # Not JSON, but that's okay - other indicators might still match
            pass
    
    return result
