"""
Configuration file for AI Log Analyzer
"""

class Config:
    """Application configuration"""
    
    # Application Settings
    APP_NAME = "AI Log Analyzer"
    VERSION = "1.0.0"
    DEBUG = False
    
    # Perplexity API Settings
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    PERPLEXITY_TIMEOUT = 30  # seconds
    
    # Available Perplexity Models
    MODELS = {
        "quick": "sonar",
        "standard": "sonar",
        "deep": "sonar"
    }
    
    # Log Processing Settings
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_LOGS_IN_CONTEXT = 100
    
    # UI Settings
    THEME = "light"
    PAGE_TITLE = "AI Log Analyzer"
    PAGE_ICON = "🔍"
    
    # Analysis Settings
    DEFAULT_ANALYSIS_DEPTH = "Standard"
    AUTO_DETECT_USER = True
    
    # Supported Log File Extensions
    SUPPORTED_EXTENSIONS = ['.log', '.txt', '.json']
    
    # Common log patterns (regex)
    LOG_PATTERNS = {
        'timestamp': r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}',
        'log_level': r'\b(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\b',
        'api_endpoint': r'(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s]*)',
        'status_code': r'\b(1\d{2}|2\d{2}|3\d{2}|4\d{2}|5\d{2})\b',
        'user_id': r'user[_-]?id[=:\s]+([^\s,]+)',
        'username': r'username[=:\s]+([^\s,]+)',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'trace_id': r'trace[_-]?id[=:\s]+([a-zA-Z0-9-]+)',
        'request_id': r'request[_-]?id[=:\s]+([a-zA-Z0-9-]+)',
        'session_id': r'session[_-]?id[=:\s]+([a-zA-Z0-9-]+)',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'exception': r'(Exception|Error|Traceback)',
    }
    
    # Quick Action Prompts
    QUICK_ACTIONS = {
        "find_errors": "Find all errors and exceptions in the logs",
        "list_users": "List all unique users found in the logs",
        "api_summary": "Provide a summary of all API calls and their status",
        "error_patterns": "Identify common error patterns and their root causes"
    }
    
    @staticmethod
    def get_model(depth: str = "standard") -> str:
        """Get Perplexity model name based on analysis depth"""
        return Config.MODELS.get(depth.lower(), Config.MODELS["standard"])
