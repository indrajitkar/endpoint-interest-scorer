"""
Scorer module for Endpoint Interest Scorer.
Responsible for calculating interest scores and assigning risk levels.
"""

from config import SCORE_WEIGHTS, RISK_THRESHOLDS
from utils import check_keywords, has_url_parameters


def calculate_score(status_code, url, body_preview, headers):
    """
    Calculate interest score based on various factors.
    
    Args:
        status_code (int): HTTP status code
        url (str): URL being scored
        body_preview (str): Preview of response body
        headers (dict): Response headers
        
    Returns:
        int: Total score
    """
    score = 0
    
    # Score based on status code
    if status_code == 200:
        score += SCORE_WEIGHTS['status_200']
    elif status_code in [401, 403]:
        score += SCORE_WEIGHTS['status_401']  # Same weight for both
    elif status_code == 500:
        score += SCORE_WEIGHTS['status_500']
    
    # Score for URL parameters
    if has_url_parameters(url):
        score += SCORE_WEIGHTS['has_parameters']
    
    # Score for keywords in URL
    url_keywords = check_keywords(url)
    score += len(url_keywords) * SCORE_WEIGHTS['keyword_match']
    
    # Score for keywords in body preview
    body_keywords = check_keywords(body_preview)
    score += len(body_keywords) * SCORE_WEIGHTS['keyword_match']
    
    # Score for keywords in headers (convert headers dict to string)
    headers_str = str(headers).lower()
    header_keywords = check_keywords(headers_str)
    score += len(header_keywords) * SCORE_WEIGHTS['keyword_match']
    
    return score


def assign_risk_level(score):
    """
    Assign risk level based on total score.
    
    Args:
        score (int): Total interest score
        
    Returns:
        str: Risk level (Low, Medium, High, Very High)
    """
    if score >= RISK_THRESHOLDS['Very High']:
        return 'Very High'
    elif score >= RISK_THRESHOLDS['High']:
        return 'High'
    elif score >= RISK_THRESHOLDS['Medium']:
        return 'Medium'
    else:
        return 'Low'


def score_endpoint(scan_result, is_api):
    """
    Score an endpoint if it's detected as an API.
    
    Args:
        scan_result (dict): Result from scanner module
        is_api (bool): Whether endpoint was detected as API
        
    Returns:
        dict: Dictionary containing:
            - score: Total interest score (0 if not API)
            - risk_level: Risk level assignment
            - matched_keywords: List of matched keywords
    """
    result = {
        'score': 0,
        'risk_level': 'Low',
        'matched_keywords': [],
    }
    
    # Only score if it's an API endpoint
    if not is_api:
        return result
    
    # Calculate score
    score = calculate_score(
        status_code=scan_result.get('status_code'),
        url=scan_result.get('url', ''),
        body_preview=scan_result.get('body_preview', ''),
        headers=scan_result.get('headers', {})
    )
    
    result['score'] = score
    
    # Assign risk level
    result['risk_level'] = assign_risk_level(score)
    
    # Collect all matched keywords
    url = scan_result.get('url', '')
    body_preview = scan_result.get('body_preview', '')
    headers_str = str(scan_result.get('headers', {})).lower()
    
    url_keywords = check_keywords(url)
    body_keywords = check_keywords(body_preview)
    header_keywords = check_keywords(headers_str)
    
    # Combine and deduplicate keywords
    all_keywords = list(set(url_keywords + body_keywords + header_keywords))
    result['matched_keywords'] = all_keywords
    
    return result
