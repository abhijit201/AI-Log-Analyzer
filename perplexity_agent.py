import requests
import json
from typing import List, Dict, Any

class PerplexityAgent:
    """AI Agent using Perplexity API for log analysis"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # System prompt for log analysis
        self.system_prompt = """You are an expert log analysis assistant. Your role is to:

1. Analyze application logs to identify errors, exceptions, and issues
2. Track user journeys through API calls
3. Identify patterns and correlations in errors
4. Pinpoint where things went wrong in API sequences
5. Provide actionable insights and recommendations

When analyzing logs:
- Look for common identifiers (user_id, username, trace_id, request_id, session_id, IP addresses)
- Track API call sequences for specific users
- Identify the transition point from successful to failed requests
- Analyze error messages and exceptions
- Consider timing and sequence of events
- Provide clear, concise explanations

Always structure your responses with:
- Summary of findings
- Specific details (line numbers, timestamps, API endpoints)
- Root cause analysis
- Recommendations for fixing the issue
"""
    
    def analyze_logs(
        self, 
        user_query: str, 
        log_data: List[Dict[str, Any]], 
        log_processor,
        analysis_depth: str = "Standard",
        auto_detect_user: bool = True
    ) -> str:
        """Analyze logs based on user query using Perplexity API"""
        
        # Prepare context from logs
        context = self._prepare_analysis_context(
            user_query, 
            log_data, 
            log_processor, 
            analysis_depth,
            auto_detect_user
        )
        
        # Build messages for API call
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context}
        ]
        
        # Determine model based on analysis depth
        model = self._get_model_for_depth(analysis_depth)
        
        # Call Perplexity API
        try:
            response = self._call_perplexity_api(messages, model)
            return response
        except Exception as e:
            return f"Error analyzing logs: {str(e)}"
    
    def _prepare_analysis_context(
        self,
        user_query: str,
        log_data: List[Dict[str, Any]],
        log_processor,
        analysis_depth: str,
        auto_detect_user: bool
    ) -> str:
        """Prepare comprehensive context for AI analysis"""
        
        context = f"USER QUERY: {user_query}\n\n"
        
        # Get statistics
        stats = log_processor.get_statistics()
        context += f"""OVERALL STATISTICS:
- Total Logs: {stats['total_logs']}
- Errors Found: {stats['errors']}
- Warnings: {stats['warnings']}
- API Calls: {stats['api_calls']}
- Unique Users: {stats['unique_users']}
- Status Code Distribution: {dict(stats['status_codes'])}

"""
        
        # Extract user identifier from query if present
        user_identifier = None
        if auto_detect_user:
            user_identifier = self._extract_user_from_query(user_query, log_processor)
        
        # If specific user mentioned, provide their journey
        if user_identifier:
            context += f"\nUSER JOURNEY ANALYSIS FOR: {user_identifier}\n"
            user_journey = log_processor.get_user_journey(user_identifier)
            error_sequence = log_processor.find_error_sequence(user_identifier)
            
            context += f"""
Journey Summary:
- Total Requests: {error_sequence['total_requests']}
- Successful: {len(error_sequence['successful_requests'])}
- Failed: {len(error_sequence['failed_requests'])}
- First Error At: {error_sequence['first_error']['line_number'] if error_sequence['first_error'] else 'None'}
- Last Successful API: {error_sequence['last_successful_api'] if error_sequence['last_successful_api'] else 'None'}

Detailed Journey:
"""
            for log in user_journey:
                context += f"Line {log['line_number']}: [{log['level']}] {log['raw'][:150]}\n"
            
            context += "\n"
        
        # Add API summary
        api_summary = log_processor.get_api_summary()
        context += f"\nAPI ENDPOINT SUMMARY:\n"
        for endpoint, stats in api_summary.items():
            context += f"- {endpoint}: {stats['total_calls']} calls, {stats['successful']} success, {stats['failed']} failed\n"
        
        # Add error patterns
        patterns = log_processor.find_common_patterns()
        context += f"\nERROR PATTERNS:\n"
        context += f"Most Common Exceptions: {patterns['most_common_exceptions']}\n"
        context += f"Most Failed APIs: {patterns['most_failed_apis']}\n"
        context += f"Affected Users: {len(patterns['affected_users'])} users\n\n"
        
        # Add relevant log samples based on query
        context += self._get_relevant_logs(user_query, log_data, analysis_depth)
        
        context += "\n\nBased on this log data, please provide a detailed analysis addressing the user's query."
        
        return context
    
    def _extract_user_from_query(self, query: str, log_processor) -> str:
        """Extract user identifier from query"""
        query_lower = query.lower()
        
        # Check if query mentions specific user
        for user in log_processor.get_all_users():
            if user.lower() in query_lower:
                return user
        
        # Look for patterns like "user john" or "username: john"
        import re
        patterns = [
            r'user\s+(\w+)',
            r'username[:\s]+(\w+)',
            r'for\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                potential_user = match.group(1)
                # Check if this user exists in logs
                for user in log_processor.get_all_users():
                    if potential_user in user.lower():
                        return user
        
        return None
    
    def _get_relevant_logs(self, query: str, log_data: List[Dict[str, Any]], depth: str) -> str:
        """Get most relevant log entries based on query"""
        
        # Determine how many logs to include
        max_logs = {
            "Quick": 20,
            "Standard": 50,
            "Deep": 100
        }.get(depth, 50)
        
        query_lower = query.lower()
        relevant_logs = []
        
        # Prioritize logs based on query keywords
        for log in log_data:
            relevance_score = 0
            
            # High priority for errors if query mentions errors
            if 'error' in query_lower and log['has_error']:
                relevance_score += 10
            
            # High priority for specific user if mentioned
            if any(keyword in query_lower for keyword in ['user', 'username', 'journey', 'track']):
                if log['identifiers']:
                    relevance_score += 5
            
            # Priority for API calls if query mentions APIs
            if 'api' in query_lower and log['api']:
                relevance_score += 5
            
            # Always include errors
            if log['has_error']:
                relevance_score += 3
            
            relevant_logs.append((relevance_score, log))
        
        # Sort by relevance and take top N
        relevant_logs.sort(key=lambda x: x[0], reverse=True)
        selected_logs = [log for _, log in relevant_logs[:max_logs]]
        
        # Format logs
        context = "RELEVANT LOG ENTRIES:\n"
        for log in selected_logs:
            context += f"\nLine {log['line_number']} [{log['level']}]"
            if log['timestamp']:
                context += f" {log['timestamp']}"
            if log['api']:
                context += f" {log['api']['method']} {log['api']['endpoint']}"
            if log['status_code']:
                context += f" [{log['status_code']}]"
            context += f"\n{log['raw']}\n"
        
        return context
    
    def _get_model_for_depth(self, depth: str) -> str:
        """Get appropriate Perplexity model based on analysis depth"""
        models = {
        "quick": "sonar",
        "standard": "sonar",
        "deep": "sonar"
        }
        return models.get(depth, "sonar")
    
    def _call_perplexity_api(self, messages: List[Dict[str, str]], model: str) -> str:
        """Make API call to Perplexity"""
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 2000,
            "stream": False
        }
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def suggest_next_steps(self, analysis_result: str) -> List[str]:
        """Suggest follow-up questions or actions based on analysis"""
        
        suggestions = []
        
        if 'error' in analysis_result.lower():
            suggestions.append("Get more details about the specific error")
            suggestions.append("Check if other users are affected by the same issue")
        
        if 'api' in analysis_result.lower():
            suggestions.append("Analyze the complete API call chain")
            suggestions.append("Check API response times and performance")
        
        if 'user' in analysis_result.lower():
            suggestions.append("View the complete user journey")
            suggestions.append("Compare with other users' behavior")
        
        return suggestions
