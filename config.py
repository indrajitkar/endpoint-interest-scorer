"""
Configuration file for Endpoint Interest Scorer.
Contains score weights, keywords, and risk thresholds.
"""

# Score weights for different indicators
SCORE_WEIGHTS = {
    'status_200': 5,          # Successful response
    'status_401': 10,         # Unauthorized - indicates auth required
    'status_403': 10,         # Forbidden - indicates access control
    'status_500': 15,         # Server error - potential vulnerability
    'has_parameters': 3,      # URL has query parameters
    'keyword_match': 5,      # Per keyword match
}

# Keywords that indicate interesting endpoints
KEYWORDS = [
    'admin',
    'auth',
    'login',
    'token',
    'debug',
    'config',
    'secret',
    'password',
    'api',
    'key',
    'credential',
    'session',
]

# API URL patterns to detect
API_PATTERNS = [
    '/api/',
    '/v1/',
    '/v2/',
    '/v3/',
    '/rest/',
    '/graphql',
    '/graphiql',
]

# Risk level thresholds based on total score
RISK_THRESHOLDS = {
    'Low': 0,
    'Medium': 10,
    'High': 20,
    'Very High': 30,
}

# HTTP request settings
REQUEST_TIMEOUT = 10  # seconds
MAX_BODY_PREVIEW = 500  # characters
