import re
import json
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

class LogProcessor:
    """Processes and analyzes log files"""
    
    def __init__(self):
        self.logs = []
        self.user_sessions = defaultdict(list)
        self.errors = []
        self.api_calls = []
        
        # Common patterns for log parsing
        self.patterns = {
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
    
    def parse_logs(self, content: str) -> List[Dict[str, Any]]:
        """Parse log file content into structured data"""
        lines = content.split('\n')
        parsed_logs = []
        
        for idx, line in enumerate(lines):
            if not line.strip():
                continue
            
            log_entry = {
                'line_number': idx + 1,
                'raw': line,
                'timestamp': self._extract_timestamp(line),
                'level': self._extract_log_level(line),
                'api': self._extract_api_call(line),
                'status_code': self._extract_status_code(line),
                'identifiers': self._extract_identifiers(line),
                'has_error': self._has_error(line),
                'exception_type': self._extract_exception(line)
            }
            
            parsed_logs.append(log_entry)
            
            # Track errors
            if log_entry['has_error']:
                self.errors.append(log_entry)
            
            # Track API calls
            if log_entry['api']:
                self.api_calls.append(log_entry)
            
            # Group by user identifiers
            for identifier_type, identifier_value in log_entry['identifiers'].items():
                if identifier_value:
                    self.user_sessions[identifier_value].append(log_entry)
        
        self.logs = parsed_logs
        return parsed_logs
    
    def _extract_timestamp(self, line: str) -> str:
        """Extract timestamp from log line"""
        match = re.search(self.patterns['timestamp'], line)
        return match.group(0) if match else None
    
    def _extract_log_level(self, line: str) -> str:
        """Extract log level (INFO, ERROR, etc.)"""
        match = re.search(self.patterns['log_level'], line, re.IGNORECASE)
        return match.group(1).upper() if match else 'INFO'
    
    def _extract_api_call(self, line: str) -> Dict[str, str]:
        """Extract API method and endpoint"""
        match = re.search(self.patterns['api_endpoint'], line)
        if match:
            return {
                'method': match.group(1),
                'endpoint': match.group(2)
            }
        return None
    
    def _extract_status_code(self, line: str) -> int:
        """Extract HTTP status code"""
        match = re.search(self.patterns['status_code'], line)
        if match:
            code = int(match.group(1))
            # Only return if it's a valid HTTP status code
            if 100 <= code <= 599:
                return code
        return None
    
    def _extract_identifiers(self, line: str) -> Dict[str, str]:
        """Extract user identifiers (user_id, username, trace_id, etc.)"""
        identifiers = {}
        
        for key in ['user_id', 'username', 'email', 'trace_id', 'request_id', 'session_id', 'ip_address']:
            match = re.search(self.patterns[key], line, re.IGNORECASE)
            if match:
                if key in ['user_id', 'username', 'trace_id', 'request_id', 'session_id']:
                    identifiers[key] = match.group(1)
                else:
                    identifiers[key] = match.group(0)
        
        return identifiers
    
    def _has_error(self, line: str) -> bool:
        """Check if line contains error or exception"""
        return bool(re.search(self.patterns['exception'], line, re.IGNORECASE)) or \
               'error' in line.lower() or 'exception' in line.lower()
    
    def _extract_exception(self, line: str) -> str:
        """Extract exception type"""
        # Look for common exception patterns
        exception_pattern = r'(\w+Exception|\w+Error)'
        match = re.search(exception_pattern, line)
        return match.group(1) if match else None
    
    def get_user_journey(self, user_identifier: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific user"""
        # Search across all identifier types
        user_logs = []
        
        for logs in self.user_sessions.values():
            for log in logs:
                for identifier_value in log['identifiers'].values():
                    if identifier_value and user_identifier.lower() in str(identifier_value).lower():
                        user_logs.append(log)
                        break
        
        # Sort by timestamp
        user_logs.sort(key=lambda x: x['timestamp'] or '')
        return user_logs
    
    def find_error_sequence(self, user_identifier: str) -> Dict[str, Any]:
        """Find where user started experiencing errors"""
        user_logs = self.get_user_journey(user_identifier)
        
        if not user_logs:
            return None
        
        result = {
            'total_requests': len(user_logs),
            'successful_requests': [],
            'failed_requests': [],
            'first_error': None,
            'last_successful_api': None,
            'error_apis': []
        }
        
        for log in user_logs:
            if log['has_error'] or (log['status_code'] and log['status_code'] >= 400):
                result['failed_requests'].append(log)
                if not result['first_error']:
                    result['first_error'] = log
                if log['api']:
                    result['error_apis'].append(log['api'])
            else:
                result['successful_requests'].append(log)
                if log['api']:
                    result['last_successful_api'] = log['api']
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        stats = {
            'total_logs': len(self.logs),
            'errors': len([l for l in self.logs if l['has_error']]),
            'warnings': len([l for l in self.logs if l['level'] == 'WARN']),
            'api_calls': len(self.api_calls),
            'unique_users': len(self.user_sessions),
            'status_codes': defaultdict(int)
        }
        
        for log in self.logs:
            if log['status_code']:
                stats['status_codes'][log['status_code']] += 1
        
        return stats
    
    def get_all_users(self) -> List[str]:
        """Get list of all unique user identifiers"""
        return list(self.user_sessions.keys())
    
    def get_api_summary(self) -> Dict[str, Any]:
        """Get summary of all API calls"""
        api_stats = defaultdict(lambda: {
            'total_calls': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        })
        
        for log in self.api_calls:
            if log['api']:
                endpoint = f"{log['api']['method']} {log['api']['endpoint']}"
                api_stats[endpoint]['total_calls'] += 1
                
                if log['status_code'] and log['status_code'] < 400:
                    api_stats[endpoint]['successful'] += 1
                elif log['has_error'] or (log['status_code'] and log['status_code'] >= 400):
                    api_stats[endpoint]['failed'] += 1
                    if log['exception_type']:
                        api_stats[endpoint]['errors'].append(log['exception_type'])
        
        return dict(api_stats)
    
    def find_common_patterns(self) -> Dict[str, Any]:
        """Find common error patterns"""
        error_patterns = {
            'most_common_exceptions': defaultdict(int),
            'most_failed_apis': defaultdict(int),
            'error_by_status_code': defaultdict(int),
            'affected_users': set()
        }
        
        for log in self.errors:
            if log['exception_type']:
                error_patterns['most_common_exceptions'][log['exception_type']] += 1
            
            if log['api']:
                endpoint = f"{log['api']['method']} {log['api']['endpoint']}"
                error_patterns['most_failed_apis'][endpoint] += 1
            
            if log['status_code']:
                error_patterns['error_by_status_code'][log['status_code']] += 1
            
            for identifier_value in log['identifiers'].values():
                if identifier_value:
                    error_patterns['affected_users'].add(identifier_value)
        
        # Convert to regular dict for JSON serialization
        return {
            'most_common_exceptions': dict(error_patterns['most_common_exceptions']),
            'most_failed_apis': dict(error_patterns['most_failed_apis']),
            'error_by_status_code': dict(error_patterns['error_by_status_code']),
            'affected_users': list(error_patterns['affected_users'])
        }
    
    def prepare_context_for_ai(self, max_logs: int = 100) -> str:
        """Prepare log data as context for AI analysis"""
        stats = self.get_statistics()
        api_summary = self.get_api_summary()
        patterns = self.find_common_patterns()
        
        context = f"""
LOG ANALYSIS CONTEXT:

STATISTICS:
- Total Logs: {stats['total_logs']}
- Errors: {stats['errors']}
- Warnings: {stats['warnings']}
- API Calls: {stats['api_calls']}
- Unique Users: {stats['unique_users']}

API SUMMARY:
{json.dumps(api_summary, indent=2)}

ERROR PATTERNS:
{json.dumps(patterns, indent=2)}

RECENT LOGS (last {min(max_logs, len(self.logs))} entries):
"""
        
        # Add sample of recent logs
        recent_logs = self.logs[-max_logs:] if len(self.logs) > max_logs else self.logs
        for log in recent_logs:
            context += f"\n[{log['level']}] {log['raw'][:200]}"
        
        return context
