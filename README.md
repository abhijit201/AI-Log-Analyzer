# **📚 Knowledge Transfer Document**

## **AI Log Analyzer \- Complete Technical Documentation**

---

## **📋 Table of Contents**

1. Project Overview  
2. Architecture & Design  
3. File Structure  
4. Detailed Code Walkthrough  
5. Key Functions Explained  
6. Data Flow Diagram  
7. API Integration  
8. Testing & Troubleshooting  
9. Extension Points

---

## **1\. Project Overview**

### **1.1 Purpose**

The AI Log Analyzer is an intelligent log analysis tool that helps developers and DevOps teams:

* Automatically detect errors and exceptions in application logs  
* Track user journeys across multiple API calls  
* Identify root causes of issues  
* Analyze error patterns and trends  
* Provide AI-powered insights using Perplexity API

### **1.2 Technology Stack**

* **Frontend/UI**: Streamlit (Python web framework)  
* **AI Engine**: Perplexity API (Large Language Models)  
* **Backend**: Python 3.11/3.12  
* **Key Libraries**:  
  * `streamlit` \- Web interface  
  * `requests` \- HTTP calls to Perplexity API  
  * `re` (regex) \- Log parsing  
  * `json` \- Data handling

### **1.3 Key Features**

1. **Smart Log Parsing**: Automatically extracts structured data from unstructured logs  
2. **User Journey Tracking**: Follows user through API calls using multiple identifier types  
3. **Error Chain Analysis**: Identifies where successful requests turned into failures  
4. **AI-Powered Insights**: Uses Perplexity API for intelligent analysis  
5. **Interactive Chat Interface**: Natural language queries for log analysis  
6. **Quick Actions**: Pre-built analysis templates

---

## **2\. Architecture & Design** **2.1 System Architecture** **![][image1]**          

### **2.2 Design Patterns Used**

1. **Singleton Pattern**: Configuration class maintains single instance  
2. **Strategy Pattern**: Different analysis depths use different AI models  
3. **Observer Pattern**: Session state management in Streamlit  
4. **Factory Pattern**: Log entry creation based on content type

### **2.3 Data Flow![][image2]**

---

## **3\. File Structure**

ai-log-analyzer/  
│  
├── main.py                 \# Main application entry point (UI & orchestration)  
├── log\_processor.py        \# Log parsing and analysis logic  
├── perplexity\_agent.py     \# AI agent with Perplexity API integration  
├── config.py               \# Configuration and constants  
├── requirements.txt        \# Python dependencies  
├── sample\_logs.log         \# Example log file for testing  
├── SETUP\_GUIDE.md         \# Installation and setup instructions

└── venv/                  \# Virtual environment (not in repo)

---

## **4\. Detailed Code Walkthrough**

### **4.1 main.py \- Application Entry Point**

**Purpose**: Main Streamlit application that handles UI, user interactions, and orchestrates other components.

#### **Key Sections:**

#### **4.1.1 Imports and Configuration**

python  
import streamlit as st  
import json  
from datetime import datetime  
from config import Config  
from log\_processor import LogProcessor  
from perplexity\_agent import PerplexityAgent

*\# Page config*  
st.set\_page\_config(  
    page\_title\="AI Log Analyzer",  
    page\_icon\="🔍",  
    layout\="wide"

)

**Explanation**:

* Imports necessary modules  
* `st.set_page_config()` sets browser tab title, icon, and layout  
* `layout="wide"` uses full browser width

#### **4.1.2 Custom CSS Styling**

python  
st.markdown("""  
\<style\>  
    .main-header { ... }  
    .chat-message { ... }  
    .user-message { ... }  
    .assistant-message { ... }  
\</style\>

""", unsafe\_allow\_html\=True)

**Explanation**:

* Injects custom CSS for better UI appearance  
* `unsafe_allow_html=True` allows HTML/CSS injection  
* Styles chat bubbles, headers, and badges

#### **4.1.3 Session State Initialization**

python  
if 'messages' not in st.session\_state:  
    st.session\_state.messages \= \[\]  
if 'log\_data' not in st.session\_state:  
    st.session\_state.log\_data \= None  
if 'log\_processor' not in st.session\_state:  
    st.session\_state.log\_processor \= None  
if 'agent' not in st.session\_state:

    st.session\_state.agent \= None

**Explanation**:

* `st.session_state` persists data across reruns  
* Stores: chat history, parsed logs, processor instance, AI agent  
* Prevents re-initialization on every interaction

#### **4.1.4 Sidebar Configuration**

python  
with st.sidebar:  
    st.header("⚙️ Configuration")  
      
    api\_key \= st.text\_input(  
        "Perplexity API Key",  
        type\="password",  
        value\=st.session\_state.get('api\_key', ''),  
        help\="Enter your Perplexity API key"  
    )  
      
    if api\_key:  
        st.session\_state.api\_key \= api\_key  
        if not st.session\_state.agent:

            st.session\_state.agent \= PerplexityAgent(api\_key)

**Explanation**:

* `st.sidebar` creates left panel  
* `type="password"` masks API key input  
* Initializes `PerplexityAgent` only once when API key is provided  
* Stores API key in session for persistence

#### **4.1.5 File Upload Handler**

python  
uploaded\_file \= st.file\_uploader(  
    "Choose a log file",  
    type\=\['log', 'txt', 'json'\],  
    help\="Upload your application log file"  
)

if uploaded\_file:  
    try:  
        content \= uploaded\_file.read().decode('utf-8')  
          
        if not st.session\_state.log\_processor:  
            st.session\_state.log\_processor \= LogProcessor()  
          
        st.session\_state.log\_data \= st.session\_state.log\_processor.parse\_logs(content)  
        

        st.success(f"✅ Processed {len(st.session\_state.log\_data)} log entries")

**Explanation**:

* `file_uploader()` creates upload widget  
* `decode('utf-8')` converts bytes to string  
* Creates `LogProcessor` instance if not exists  
* Calls `parse_logs()` to extract structured data  
* Displays success message with entry count

#### **4.1.6 Chat Interface**

python  
for message in st.session\_state.messages:  
    if message\['role'\] \== 'user':  
        st.markdown(f'\<div class="chat-message user-message"\>👤 {message\["content"\]}\</div\>',   
                  unsafe\_allow\_html\=True)  
    else:  
        st.markdown(f'\<div class="chat-message assistant-message"\>🤖 {message\["content"\]}\</div\>', 

                  unsafe\_allow\_html\=True)

**Explanation**:

* Iterates through message history  
* Displays user messages with blue styling  
* Displays AI responses with gray styling  
* Uses custom CSS classes for appearance

#### **4.1.7 Query Processing**

python  
if prompt:  
    st.session\_state.messages.append({"role": "user", "content": prompt})  
      
    with st.spinner("🔍 Analyzing logs..."):  
        try:  
            response \= st.session\_state.agent.analyze\_logs(  
                prompt,  
                st.session\_state.log\_data,  
                st.session\_state.log\_processor,  
                analysis\_depth,  
                auto\_detect\_user  
            )  
            

            st.session\_state.messages.append({"role": "assistant", "content": response})

**Explanation**:

* Captures user input from `st.chat_input()`  
* Adds user message to history  
* Shows loading spinner during processing  
* Calls AI agent's `analyze_logs()` method  
* Adds AI response to history  
* `st.rerun()` refreshes UI to show new messages

#### **4.1.8 Quick Action Buttons**

python  
with col1:  
    if st.button("🔴 Find All Errors"):  
        prompt \= "Find all errors and exceptions in the logs"  
        st.session\_state.messages.append({"role": "user", "content": prompt})  
        with st.spinner("Analyzing..."):  
            response \= st.session\_state.agent.analyze\_logs(...)  
            st.session\_state.messages.append({"role": "assistant", "content": response})

        st.rerun()

**Explanation**:

* Creates 4 columns for quick action buttons  
* Pre-defines common queries  
* Automatically submits query when button clicked  
* Same processing flow as manual chat input

---

### **4.2 log\_processor.py \- Log Processing Logic**

**Purpose**: Parses unstructured log files into structured data and performs analysis.

#### **Key Classes and Methods:**

#### **4.2.1 LogProcessor Class Initialization**

python  
class LogProcessor:  
    def \_\_init\_\_(self):  
        self.logs \= \[\]  
        self.user\_sessions \= defaultdict(list)  
        self.errors \= \[\]  
        self.api\_calls \= \[\]  
          
        self.patterns \= {  
            'timestamp': r'\\d{4}-\\d{2}-\\d{2}\[\\sT\]\\d{2}:\\d{2}:\\d{2}',  
            'log\_level': r'\\b(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\\b',  
            'api\_endpoint': r'(GET|POST|PUT|DELETE|PATCH)\\s+(/\[^\\s\]\*)',  
            *\# ... more patterns*

        }

**Explanation**:

* `logs`: Stores all parsed log entries  
* `user_sessions`: Groups logs by user identifier (defaultdict for auto-initialization)  
* `errors`: Quick access to error logs  
* `api_calls`: Quick access to API-related logs  
* `patterns`: Regex patterns for extracting information

**Regex Pattern Breakdown**:

* `timestamp`: Matches `2024-10-30 10:15:23` format  
* `log_level`: Matches DEBUG, INFO, ERROR, etc.  
* `api_endpoint`: Matches HTTP method \+ URL path  
* `user_id`: Matches patterns like `user_id=123` or `user_id: 123`

#### **4.2.2 parse\_logs() Method**

python  
def parse\_logs(self, content: str) \-\> List\[Dict\[str, Any\]\]:  
    lines \= content.split('\\n')  
    parsed\_logs \= \[\]  
      
    for idx, line in enumerate(lines):  
        if not line.strip():  
            continue  
          
        log\_entry \= {  
            'line\_number': idx \+ 1,  
            'raw': line,  
            'timestamp': self.\_extract\_timestamp(line),  
            'level': self.\_extract\_log\_level(line),  
            'api': self.\_extract\_api\_call(line),  
            'status\_code': self.\_extract\_status\_code(line),  
            'identifiers': self.\_extract\_identifiers(line),  
            'has\_error': self.\_has\_error(line),  
            'exception\_type': self.\_extract\_exception(line)  
        }  
        

        parsed\_logs.append(log\_entry)

**Explanation**:

* Splits file content by newlines  
* Processes each line individually  
* Skips empty lines  
* Creates structured dictionary for each log entry  
* Calls helper methods to extract specific information  
* Returns list of dictionaries

**Data Structure Example**:

python  
{  
    'line\_number': 5,  
    'raw': '2024-10-30 10:15:23 ERROR POST /api/payment user\_id=john123 status=500',  
    'timestamp': '2024-10-30 10:15:23',  
    'level': 'ERROR',  
    'api': {'method': 'POST', 'endpoint': '/api/payment'},  
    'status\_code': 500,  
    'identifiers': {'user\_id': 'john123'},  
    'has\_error': True,  
    'exception\_type': None

}

#### **4.2.3 Extraction Helper Methods**

**\_extract\_timestamp()**

python  
def \_extract\_timestamp(self, line: str) \-\> str:  
    match \= re.search(self.patterns\['timestamp'\], line)

    return match.group(0) if match else None

**Explanation**:

* Uses regex to find timestamp pattern  
* Returns timestamp string or None  
* `match.group(0)` gets the matched text

**\_extract\_log\_level()**

python  
def \_extract\_log\_level(self, line: str) \-\> str:  
    match \= re.search(self.patterns\['log\_level'\], line, re.IGNORECASE)

    return match.group(1).upper() if match else 'INFO'

**Explanation**:

* Searches for log level keywords  
* Case-insensitive search with `re.IGNORECASE`  
* Defaults to 'INFO' if not found  
* Returns uppercase version for consistency

**\_extract\_api\_call()**

python  
def \_extract\_api\_call(self, line: str) \-\> Dict\[str, str\]:  
    match \= re.search(self.patterns\['api\_endpoint'\], line)  
    if match:  
        return {  
            'method': match.group(1),  
            'endpoint': match.group(2)  
        }

    return None

**Explanation**:

* Extracts HTTP method (GET, POST, etc.) and URL path  
* Returns dictionary with both pieces  
* Returns None if no API call found  
* `match.group(1)` \= method, `match.group(2)` \= endpoint

**\_extract\_identifiers()**

python  
def \_extract\_identifiers(self, line: str) \-\> Dict\[str, str\]:  
    identifiers \= {}  
      
    for key in \['user\_id', 'username', 'email', 'trace\_id', 'request\_id', 'session\_id', 'ip\_address'\]:  
        match \= re.search(self.patterns\[key\], line, re.IGNORECASE)  
        if match:  
            if key in \['user\_id', 'username', 'trace\_id', 'request\_id', 'session\_id'\]:  
                identifiers\[key\] \= match.group(1)  
            else:  
                identifiers\[key\] \= match.group(0)  
    

    return identifiers

**Explanation**:

* Searches for multiple identifier types in one line  
* Builds dictionary of found identifiers  
* `match.group(1)` extracts captured group (value after `=` or `:`)  
* `match.group(0)` for patterns without capture groups (like email, IP)

#### **4.2.4 User Journey Tracking**

**get\_user\_journey()**

python  
def get\_user\_journey(self, user\_identifier: str) \-\> List\[Dict\[str, Any\]\]:  
    user\_logs \= \[\]  
      
    for logs in self.user\_sessions.values():  
        for log in logs:  
            for identifier\_value in log\['identifiers'\].values():  
                if identifier\_value and user\_identifier.lower() in str(identifier\_value).lower():  
                    user\_logs.append(log)  
                    break  
      
    user\_logs.sort(key\=lambda x: x\['timestamp'\] or '')

    return user\_logs

**Explanation**:

* Searches across all identifier types (flexible matching)  
* Case-insensitive search for user  
* Collects all matching log entries  
* Sorts by timestamp for chronological view  
* Returns ordered list of user's log entries

**find\_error\_sequence()**

python  
def find\_error\_sequence(self, user\_identifier: str) \-\> Dict\[str, Any\]:  
    user\_logs \= self.get\_user\_journey(user\_identifier)  
      
    result \= {  
        'total\_requests': len(user\_logs),  
        'successful\_requests': \[\],  
        'failed\_requests': \[\],  
        'first\_error': None,  
        'last\_successful\_api': None,  
        'error\_apis': \[\]  
    }  
      
    for log in user\_logs:  
        if log\['has\_error'\] or (log\['status\_code'\] and log\['status\_code'\] \>= 400):  
            result\['failed\_requests'\].append(log)  
            if not result\['first\_error'\]:  
                result\['first\_error'\] \= log  
            if log\['api'\]:  
                result\['error\_apis'\].append(log\['api'\])  
        else:  
            result\['successful\_requests'\].append(log)  
            if log\['api'\]:  
                result\['last\_successful\_api'\] \= log\['api'\]  
    

    return result

**Explanation**:

* Gets complete user journey  
* Separates successful and failed requests  
* Identifies first error occurrence (transition point)  
* Tracks last successful API before failure  
* Lists all APIs that had errors  
* Returns comprehensive error analysis

#### **4.2.5 Statistics and Patterns**

**get\_statistics()**

python  
def get\_statistics(self) \-\> Dict\[str, Any\]:  
    stats \= {  
        'total\_logs': len(self.logs),  
        'errors': len(\[l for l in self.logs if l\['has\_error'\]\]),  
        'warnings': len(\[l for l in self.logs if l\['level'\] \== 'WARN'\]),  
        'api\_calls': len(self.api\_calls),  
        'unique\_users': len(self.user\_sessions),  
        'status\_codes': defaultdict(int)  
    }  
      
    for log in self.logs:  
        if log\['status\_code'\]:  
            stats\['status\_codes'\]\[log\['status\_code'\]\] \+= 1  
    

    return stats

**Explanation**:

* Counts total logs, errors, warnings  
* Counts API calls and unique users  
* Builds status code distribution  
* List comprehension for efficient filtering  
* Returns summary dictionary

**find\_common\_patterns()**

python  
def find\_common\_patterns(self) \-\> Dict\[str, Any\]:  
    error\_patterns \= {  
        'most\_common\_exceptions': defaultdict(int),  
        'most\_failed\_apis': defaultdict(int),  
        'error\_by\_status\_code': defaultdict(int),  
        'affected\_users': set()  
    }  
      
    for log in self.errors:  
        if log\['exception\_type'\]:  
            error\_patterns\['most\_common\_exceptions'\]\[log\['exception\_type'\]\] \+= 1  
          
        if log\['api'\]:  
            endpoint \= f"{log\['api'\]\['method'\]} {log\['api'\]\['endpoint'\]}"  
            error\_patterns\['most\_failed\_apis'\]\[endpoint\] \+= 1  
          
        if log\['status\_code'\]:  
            error\_patterns\['error\_by\_status\_code'\]\[log\['status\_code'\]\] \+= 1  
          
        for identifier\_value in log\['identifiers'\].values():  
            if identifier\_value:  
                error\_patterns\['affected\_users'\].add(identifier\_value)  
      
    return {  
        'most\_common\_exceptions': dict(error\_patterns\['most\_common\_exceptions'\]),  
        'most\_failed\_apis': dict(error\_patterns\['most\_failed\_apis'\]),  
        'error\_by\_status\_code': dict(error\_patterns\['error\_by\_status\_code'\]),  
        'affected\_users': list(error\_patterns\['affected\_users'\])

    }

**Explanation**:

* Analyzes error logs only  
* Counts exception types to find most common  
* Identifies problematic API endpoints  
* Groups errors by HTTP status code  
* Collects unique affected users (set prevents duplicates)  
* Converts defaultdict/set to regular dict/list for JSON serialization

---

### **4.3 perplexity\_agent.py \- AI Agent**

**Purpose**: Integrates with Perplexity API to provide intelligent log analysis using Large Language Models.

#### **4.3.1 PerplexityAgent Initialization**

python  
class PerplexityAgent:  
    def \_\_init\_\_(self, api\_key: str):  
        self.api\_key \= api\_key  
        self.base\_url \= "https://api.perplexity.ai/chat/completions"  
        self.headers \= {  
            "Authorization": f"Bearer {api\_key}",  
            "Content-Type": "application/json"  
        }  
        

        self.system\_prompt \= """You are an expert log analysis assistant..."""

**Explanation**:

* Stores API key for authentication  
* Sets Perplexity API endpoint URL  
* Configures HTTP headers with Bearer token  
* Defines system prompt that instructs AI behavior  
* System prompt is sent with every request

**System Prompt Breakdown**:

* Defines AI's role and expertise  
* Lists specific analysis tasks  
* Provides analysis methodology  
* Specifies output format requirements

#### **4.3.2 analyze\_logs() \- Main Analysis Method**

python  
def analyze\_logs(  
    self,   
    user\_query: str,   
    log\_data: List\[Dict\[str, Any\]\],   
    log\_processor,  
    analysis\_depth: str \= "Standard",  
    auto\_detect\_user: bool \= True  
) \-\> str:  
    context \= self.\_prepare\_analysis\_context(  
        user\_query,   
        log\_data,   
        log\_processor,   
        analysis\_depth,  
        auto\_detect\_user  
    )  
      
    messages \= \[  
        {"role": "system", "content": self.system\_prompt},  
        {"role": "user", "content": context}  
    \]  
      
    model \= self.\_get\_model\_for\_depth(analysis\_depth)  
      
    try:  
        response \= self.\_call\_perplexity\_api(messages, model)  
        return response  
    except Exception as e:

        return f"Error analyzing logs: {str(e)}"

**Explanation**:

* Entry point for AI analysis  
* Prepares comprehensive context from logs  
* Builds message array for API (system \+ user)  
* Selects appropriate AI model based on depth  
* Makes API call and returns response  
* Error handling with try-except

**Message Structure**:

python  
\[  
    {"role": "system", "content": "You are an expert..."},  
    {"role": "user", "content": "LOG DATA:\\n Statistics...\\n User Journey...\\n"}

\]

#### **4.3.3 \_prepare\_analysis\_context() \- Context Builder**

python  
def \_prepare\_analysis\_context(  
    self,  
    user\_query: str,  
    log\_data: List\[Dict\[str, Any\]\],  
    log\_processor,  
    analysis\_depth: str,  
    auto\_detect\_user: bool  
) \-\> str:  
    context \= f"USER QUERY: {user\_query}\\n\\n"  
      
    stats \= log\_processor.get\_statistics()  
    context \+= f"""OVERALL STATISTICS:  
\- Total Logs: {stats\['total\_logs'\]}  
\- Errors Found: {stats\['errors'\]}  
\- Warnings: {stats\['warnings'\]}  
...  
"""  
      
    user\_identifier \= None  
    if auto\_detect\_user:  
        user\_identifier \= self.\_extract\_user\_from\_query(user\_query, log\_processor)  
      
    if user\_identifier:  
        context \+= f"\\nUSER JOURNEY ANALYSIS FOR: {user\_identifier}\\n"  
        user\_journey \= log\_processor.get\_user\_journey(user\_identifier)  
        error\_sequence \= log\_processor.find\_error\_sequence(user\_identifier)  
        *\# ... add journey details*  
      
    api\_summary \= log\_processor.get\_api\_summary()  
    context \+= f"\\nAPI ENDPOINT SUMMARY:\\n..."  
      
    patterns \= log\_processor.find\_common\_patterns()  
    context \+= f"\\nERROR PATTERNS:\\n..."  
      
    context \+= self.\_get\_relevant\_logs(user\_query, log\_data, analysis\_depth)  
    

    return context

**Explanation**:

* Builds comprehensive context string for AI  
* Starts with user's actual query  
* Adds overall statistics for context  
* Attempts to extract user from query  
* If user found, adds complete journey analysis  
* Includes API summary and error patterns  
* Adds relevant log samples  
* Returns formatted string ready for API

**Context Structure Example**:

USER QUERY: Find errors for user john123

OVERALL STATISTICS:  
\- Total Logs: 150  
\- Errors: 12  
...

USER JOURNEY ANALYSIS FOR: john123  
Journey Summary:  
\- Total Requests: 8  
\- Successful: 5  
\- Failed: 3  
...

Detailed Journey:  
Line 5: \[INFO\] 2024-10-30 10:15:23 GET /api/login...  
Line 8: \[ERROR\] 2024-10-30 10:16:30 POST /api/checkout...

API ENDPOINT SUMMARY:  
\- POST /api/checkout: 10 calls, 7 success, 3 failed

ERROR PATTERNS:  
Most Common Exceptions: {'PaymentGatewayException': 5}  
...

RELEVANT LOG ENTRIES:  
Line 8 \[ERROR\] 2024-10-30 10:16:30 POST /api/checkout \[500\]

...

#### **4.3.4 \_extract\_user\_from\_query()**

python  
def \_extract\_user\_from\_query(self, query: str, log\_processor) \-\> str:  
    query\_lower \= query.lower()  
      
    for user in log\_processor.get\_all\_users():  
        if user.lower() in query\_lower:  
            return user  
      
    import re  
    patterns \= \[  
        r'user\\s+(\\w+)',  
        r'username\[:\\s\]+(\\w+)',  
        r'for\\s+(\\w+)',  
    \]  
      
    for pattern in patterns:  
        match \= re.search(pattern, query\_lower)  
        if match:  
            potential\_user \= match.group(1)  
            for user in log\_processor.get\_all\_users():  
                if potential\_user in user.lower():  
                    return user  
    

    return None

**Explanation**:

* Extracts user identifier from natural language query  
* First checks if any known user is directly mentioned  
* Then uses regex patterns to find user references  
* Matches patterns like "user john", "username: alice", "for bob"  
* Returns first matching user or None  
* Enables queries like "Find errors for john123"

#### **4.3.5 \_get\_relevant\_logs()**

python  
def \_get\_relevant\_logs(self, query: str, log\_data: List\[Dict\[str, Any\]\], depth: str) \-\> str:  
    max\_logs \= {  
        "Quick": 20,  
        "Standard": 50,  
        "Deep": 100  
    }.get(depth, 50)  
      
    query\_lower \= query.lower()  
    relevant\_logs \= \[\]  
      
    for log in log\_data:  
        relevance\_score \= 0  
          
        if 'error' in query\_lower and log\['has\_error'\]:  
            relevance\_score \+= 10  
          
        if any(keyword in query\_lower for keyword in \['user', 'username', 'journey', 'track'\]):  
            if log\['identifiers'\]:  
                relevance\_score \+= 5  
          
        if 'api' in query\_lower and log\['api'\]:  
            relevance\_score \+= 5  
          
        if log\['has\_error'\]:  
            relevance\_score \+= 3  
          
        relevant\_logs.append((relevance\_score, log))  
      
    relevant\_logs.sort(key\=lambda x: x\[0\], reverse\=True)  
    selected\_logs \= \[log for \_, log in relevant\_logs\[:max\_logs\]\]  
      
    context \= "RELEVANT LOG ENTRIES:\\n"  
    for log in selected\_logs:  
        context \+= f"\\nLine {log\['line\_number'\]} \[{log\['level'\]}\]"  
        if log\['timestamp'\]:  
            context \+= f" {log\['timestamp'\]}"  
        if log\['api'\]:  
            context \+= f" {log\['api'\]\['method'\]} {log\['api'\]\['endpoint'\]}"  
        if log\['status\_code'\]:  
            context \+= f" \[{log\['status\_code'\]}\]"  
        context \+= f"\\n{log\['raw'\]}\\n"  
    

    return context

**Explanation**:

* Intelligently selects most relevant logs based on query  
* Limits number based on analysis depth  
* Assigns relevance scores to each log  
* Higher scores for logs matching query keywords  
* Always prioritizes error logs  
* Sorts by relevance, takes top N  
* Formats logs for AI context  
* Prevents sending unnecessary data to API

**Scoring Logic**:

* Error in query \+ error log \= \+10 points  
* User-related query \+ has identifiers \= \+5 points  
* API in query \+ has API call \= \+5 points  
* Any error log \= \+3 points (always relevant)

#### **4.3.6 \_call\_perplexity\_api()**

python  
def \_call\_perplexity\_api(self, messages: List\[Dict\[str, str\]\], model: str) \-\> str:  
    payload \= {  
        "model": model,  
        "messages": messages,  
        "temperature": 0.2,  
        "max\_tokens": 2000,  
        "stream": False  
    }  
      
    response \= requests.post(  
        self.base\_url,  
        headers\=self.headers,  
        json\=payload,  
        timeout\=30  
    )  
      
    if response.status\_code \== 200:  
        result \= response.json()  
        return result\['choices'\]\[0\]\['message'\]\['content'\]  
    else:

        raise Exception(f"API Error: {response.status\_code} \- {response.text}")

**Explanation**:

* Makes HTTP POST request to Perplexity API  
* `temperature=0.2`: Low randomness for consistent analysis  
* `max_tokens=2000`: Response length limit  
* `stream=False`: Get complete response at once  
* `timeout=30`: 30-second request timeout  
* Returns AI-generated response text  
* Raises exception on API errors

**API Parameters**:

* **model**: Which AI model to use (small/large)  
* **messages**: Conversation history (system \+ user)  
* **temperature**: Creativity level (0.0-1.0, lower \= more focused)  
* **max\_tokens**: Maximum response length  
* **stream**: Whether to stream response chunks

**Response Structure**:

json  
{  
  "choices": \[  
    {  
      "message": {  
        "role": "assistant",  
        "content": "Analysis result text..."  
      }  
    }  
  \]

}

#### **4.3.7 \_get\_model\_for\_depth()**

python  
def \_get\_model\_for\_depth(self, depth: str) \-\> str:  
    models \= {  
        "Quick": "llama-3.1-sonar-small-128k-online",  
        "Standard": "llama-3.1-sonar-large-128k-online",  
        "Deep": "llama-3.1-sonar-large-128k-online"  
    }

    return models.get(depth, "llama-3.1-sonar-large-128k-online")

**Explanation**:

* Maps analysis depth to appropriate AI model  
* **Quick**: Smaller, faster model for basic analysis  
* **Standard/Deep**: Larger model for comprehensive analysis  
* Returns default if depth not recognized  
* Balances speed vs. quality

---

### **4.4 config.py \- Configuration Management**

**Purpose**: Centralized configuration for easy maintenance and updates.

python  
class Config:  
    *\# Application Settings*  
    APP\_NAME \= "AI Log Analyzer"  
    VERSION \= "1.0.0"  
    DEBUG \= False  
      
    *\# Perplexity API Settings*  
    PERPLEXITY\_API\_URL \= "https://api.perplexity.ai/chat/completions"  
    PERPLEXITY\_TIMEOUT \= 30  
      
    *\# Available Models*  
    MODELS \= {  
        "quick": "llama-3.1-sonar-small-128k-online",  
        "standard": "llama-3.1-sonar-large-128k-online",  
        "deep": "llama-3.1-sonar-large-128k-online"  
    }  
      
    *\# Log Processing Settings*  
    MAX\_LOG\_SIZE \= 10 \* 1024 \* 1024  *\# 10 MB*  
    MAX\_LOGS\_IN\_CONTEXT \= 100  
      
    *\# Log Patterns*  
    LOG\_PATTERNS \= {  
        'timestamp': r'\\d{4}-\\d{2}-\\d{2}\[\\sT\]\\d{2}:\\d{2}:\\d{2}',  
        'log\_level': r'\\b(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\\b',  
        *\# ... more patterns*

    }

**Explanation**:

* Static configuration class (no instances needed)  
* All constants in one place for easy updates  
* API URLs, timeouts, model names  
* Regex patterns for log parsing  
* File size limits  
* Quick Actions templates

**Benefits**:

* Single source of truth  
* Easy to update API endpoints  
* No hardcoded values in business logic  
* Can be extended with environment variables

---

## **5\. Key Functions Explained**

### **5.1 Session State Management**

**What is it?** Streamlit reruns the entire script on every interaction. Session state preserves data between reruns.

**How it works:**

python  
*\# Initialize*  
if 'messages' not in st.session\_state:  
    st.session\_state.messages \= \[\]

*\# Use*  
st.session\_state.messages.append({"role": "user", "content": "Hello"})

*\# Access*  
for msg in st.session\_state.messages:

    print(msg)

**Why it's needed:**

* Preserve chat history  
* Keep uploaded log data  
* Maintain processor/agent instances  
* Remember user settings

### **5.2 Regex Pattern Matching**

**Purpose**: Extract structured data from unstructured text.

**Example**:

python  
*\# Pattern*  
pattern \= r'user\_id\[=:\\s\]+(\[^\\s,\]+)'

*\# Text*  
text \= "Request received user\_id=john123 status=200"

*\# Match*  
match \= re.search(pattern, text)

result \= match.group(1)  *\# Returns: "john123"*

**Pattern Breakdown**:

* `user_id`: Literal text  
* `[=:\s]+`: One or more of `=`, `:`, or space  
* `([^\s,]+)`: Capture group \- any chars except space/comma  
* `match.group(1)`: Returns captured text

### **5.3 DefaultDict Usage**

**Purpose**: Dictionary that auto-creates missing keys.

**Example**:

python  
from collections import defaultdict

*\# Regular dict \- KeyError if key missing*  
regular \= {}  
regular\['key'\] \+= 1  *\# ERROR\!*

*\# DefaultDict \- auto-creates with default value*  
counter \= defaultdict(int)

counter\['key'\] \+= 1  *\# Works\! Creates key with value 0, then adds 1*

**In our code**:

python  
self.user\_sessions \= defaultdict(list)

self.user\_sessions\['john123'\].append(log\_entry)  *\# Auto-creates empty list*

### **5.4 List Comprehension**

**Purpose**: Concise way to filter/transform lists.

**Example**:

python  
*\# Traditional way*  
errors \= \[\]  
for log in self.logs:  
    if log\['has\_error'\]:  
        errors.append(log)

*\# List comprehension*

errors \= \[log for log in self.logs if log\['has\_error'\]\]

**Benefits**:

* More readable  
* Faster execution  
* Single line

### **5.5 Lambda Functions**

**Purpose**: Anonymous functions for simple operations.

**Example**:

python  
*\# Sort by timestamp*  
logs.sort(key\=lambda x: x\['timestamp'\])

*\# Equivalent to:*  
def get\_timestamp(log):  
    return log\['timestamp'\]

logs.sort(key\=get\_timestamp)

**In our code**:

python  
*\# Sort by relevance score*  
relevant\_logs.sort(key\=lambda x: x\[0\], reverse\=True)

*\# x\[0\] \= relevance score, x\[1\] \= log entry*

---

## **6\. Data Flow Diagram**

### **6.1 Complete Request Flow**

USER UPLOADS FILE  
      │  
      ▼  
┌─────────────────┐  
│  Read File      │  
│  (UTF-8 decode) │  
└────────┬────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  LogProcessor       │  
│  .parse\_logs()      │  
├─────────────────────┤  
│ • Split by lines    │  
│ • Extract timestamp │  
│ • Extract level     │  
│ • Extract API       │  
│ • Extract IDs       │  
│ • Detect errors     │  
└────────┬────────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  Structured Data    │  
│  (List of Dicts)    │  
└────────┬────────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  Store in Session   │  
│  st.session\_state   │  
│  .log\_data          │  
└─────────────────────┘

USER ASKS QUESTION  
      │  
      ▼  
┌─────────────────────┐  
│  Extract User       │  
│  from Query         │  
└────────┬────────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  Get User Journey   │  
│  Get Statistics     │  
│  Get Patterns       │  
│  Get Relevant Logs  │  
└────────┬────────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  Build Context      │  
│  (Formatted String) │  
└────────┬────────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  Perplexity API     │  
│  POST Request       │  
├─────────────────────┤  
│ Headers: API Key    │  
│ Body: Messages      │  
│ Model: Based on     │  
│        depth        │  
└────────┬────────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  AI Analysis        │  
│  (JSON Response)    │  
└────────┬────────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  Extract Content    │  
│  from Response      │  
└────────┬────────────┘  
         │  
         ▼  
┌─────────────────────┐  
│  Display in Chat    │  
│  Update Messages    │  
│  st.rerun()         │

└─────────────────────┘

### **6.2 Error Handling Flow**

┌─────────────────┐  
│  User Action    │  
└────────┬────────┘  
         │  
         ▼  
    ┌────────┐  
    │ Try    │  
    └───┬────┘  
        │  
        ▼  
   ┌────────────┐      Success  
   │  Execute   ├──────────────► Continue  
   │  Operation │  
   └────┬───────┘  
        │  
        │ Exception  
        ▼  
   ┌────────────┐  
   │  Except    │  
   │  Block     │  
   └────┬───────┘  
        │  
        ▼  
   ┌────────────┐  
   │  Log Error │  
   │  Show User │  
   └────┬───────┘  
        │  
        ▼  
   ┌────────────┐  
   │  Continue  │  
   │  Gracefully│

   └────────────┘

---

## **7\. API Integration Details**

### **7.1 Perplexity API Endpoint**

**URL**: `https://api.perplexity.ai/chat/completions`

**Method**: POST

**Headers**:

json  
{  
  "Authorization": "Bearer YOUR\_API\_KEY",  
  "Content-Type": "application/json"

}

**Request Body**:

json  
{  
  "model": "llama-3.1-sonar-large-128k-online",  
  "messages": \[  
    {  
      "role": "system",  
      "content": "You are an expert log analysis assistant..."  
    },  
    {  
      "role": "user",  
      "content": "LOG DATA:\\n Statistics...\\n"  
    }  
  \],  
  "temperature": 0.2,  
  "max\_tokens": 2000,  
  "stream": false

}

**Response**:

json  
{  
  "id": "unique-id",  
  "model": "llama-3.1-sonar-large-128k-online",  
  "choices": \[  
    {  
      "index": 0,  
      "message": {  
        "role": "assistant",  
        "content": "Based on the logs, I found..."  
      },  
      "finish\_reason": "stop"  
    }  
  \],  
  "usage": {  
    "prompt\_tokens": 500,  
    "completion\_tokens": 300,  
    "total\_tokens": 800  
  }

}

### **7.2 Model Selection**

**Available Models**:

1. **llama-3.1-sonar-small-128k-online**  
   * Faster responses  
   * Lower cost  
   * Good for quick analysis  
   * 128K token context window  
2. **llama-3.1-sonar-large-128k-online**  
   * More accurate  
   * Better reasoning  
   * Comprehensive analysis  
   * 128K token context window

**When to use each**:

* **Small**: Quick overview, simple queries, high volume  
* **Large**: Deep analysis, complex patterns, root cause investigation

### **7.3 Rate Limits & Best Practices**

**Rate Limits** (check Perplexity docs for current limits):

* Requests per minute  
* Tokens per minute  
* Concurrent requests

**Best Practices**:

1. **Batch similar queries** \- Combine multiple questions in one context  
2. **Cache results** \- Store responses for repeated queries  
3. **Limit context size** \- Send only relevant logs  
4. **Use appropriate model** \- Don't use large model for simple queries  
5. **Handle errors gracefully** \- Implement retry logic  
6. **Monitor usage** \- Track API calls and costs

### **7.4 Error Handling**

**Common Errors**:

1. **401 Unauthorized**: Invalid API key  
2. **429 Too Many Requests**: Rate limit exceeded  
3. **500 Internal Server Error**: API issue  
4. **Timeout**: Request took too long

**Handling Code**:

python  
try:  
    response \= self.\_call\_perplexity\_api(messages, model)  
    return response  
except requests.exceptions.Timeout:  
    return "Request timed out. Try with fewer logs or Quick analysis."  
except requests.exceptions.HTTPError as e:  
    if e.response.status\_code \== 429:  
        return "Rate limit reached. Please wait a moment."  
    return f"API Error: {e.response.status\_code}"  
except Exception as e:

    return f"Unexpected error: {str(e)}"

---

## **8\. Testing & Troubleshooting**

### **8.1 Unit Testing Strategy**

**Test LogProcessor**:

python  
def test\_parse\_logs():  
    processor \= LogProcessor()  
    sample\_log \= "2024-10-30 10:15:23 ERROR POST /api/payment user\_id=john123 status=500"  
    result \= processor.parse\_logs(sample\_log)  
      
    assert len(result) \== 1  
    assert result\[0\]\['level'\] \== 'ERROR'  
    assert result\[0\]\['has\_error'\] \== True

    assert result\[0\]\['identifiers'\]\['user\_id'\] \== 'john123'

**Test Pattern Extraction**:

python  
def test\_extract\_user\_id():  
    processor \= LogProcessor()  
    line \= "Request user\_id=john123 processed"  
    identifiers \= processor.\_extract\_identifiers(line)  
      
    assert 'user\_id' in identifiers

    assert identifiers\['user\_id'\] \== 'john123'

**Test User Journey**:

python  
def test\_user\_journey():  
    processor \= LogProcessor()  
    logs \= """  
    2024-10-30 10:15:23 INFO GET /api/login user\_id=john123  
    2024-10-30 10:15:45 ERROR POST /api/payment user\_id=john123  
    """  
    processor.parse\_logs(logs)  
      
    journey \= processor.get\_user\_journey('john123')  
    assert len(journey) \== 2  
    assert journey\[0\]\['api'\]\['endpoint'\] \== '/api/login'

    assert journey\[1\]\['has\_error'\] \== True

### **8.2 Common Issues & Solutions**

#### **Issue 1: Logs Not Parsing**

**Symptoms**: No logs detected after upload

**Causes**:

* Unsupported format  
* Wrong encoding  
* Empty file

**Solution**:

python  
*\# Add debug logging*  
print(f"File content length: {len(content)}")  
print(f"First 100 chars: {content\[:100\]}")

*\# Check encoding*  
try:  
    content \= uploaded\_file.read().decode('utf-8')  
except UnicodeDecodeError:

    content \= uploaded\_file.read().decode('latin-1')

#### **Issue 2: User Not Detected**

**Symptoms**: Can't find user in logs

**Causes**:

* Different identifier format  
* Typo in username  
* User not in logs

**Solution**:

python  
*\# List all found users*  
all\_users \= processor.get\_all\_users()  
st.write("Found users:", all\_users)

*\# Add more patterns*  
patterns \= \[  
    r'user\\s+(\\w+)',  
    r'username\[:\\s\]+(\\w+)',  
    r'userId\[=:\\s\]+(\\w+)',  *\# Add more variations*  
    r'usr\[=:\\s\]+(\\w+)',

\]

#### **Issue 3: API Timeout**

**Symptoms**: Request takes too long

**Causes**:

* Too many logs in context  
* Network issues  
* API overload

**Solution**:

python  
*\# Reduce context size*  
MAX\_LOGS \= 50  *\# Instead of 100*

*\# Increase timeout*  
timeout \= 60  *\# Instead of 30*

*\# Use Quick analysis*

model \= "llama-3.1-sonar-small-128k-online"

#### **Issue 4: Poor Analysis Quality**

**Symptoms**: AI gives generic or wrong answers

**Causes**:

* Insufficient context  
* Wrong model selection  
* Poor query phrasing

**Solution**:

python  
*\# Add more context*  
context \+= f"\\nFull error messages:\\n{error\_details}"

*\# Use larger model*  
model \= "llama-3.1-sonar-large-128k-online"

*\# Improve system prompt*  
self.system\_prompt \= """  
You are an expert log analyst with 10 years experience.  
Analyze logs with extreme attention to detail.  
Always cite specific line numbers and timestamps.

"""

### **8.3 Debug Mode**

**Add Debug Output**:

python  
*\# In config.py*  
DEBUG \= True

*\# In main.py*  
if Config.DEBUG:  
    st.write("Debug Info:")  
    st.write(f"Logs parsed: {len(st.session\_state.log\_data)}")  
    st.write(f"Errors found: {len(processor.errors)}")  
    st.write(f"API calls: {len(processor.api\_calls)}")

    st.write(f"Unique users: {len(processor.user\_sessions)}")

### **8.4 Performance Optimization**

**Measure Performance**:

python  
import time

start \= time.time()  
processor.parse\_logs(content)  
parse\_time \= time.time() \- start

start \= time.time()  
response \= agent.analyze\_logs(query, logs, processor)  
api\_time \= time.time() \- start

st.write(f"Parse time: {parse\_time:.2f}s")

st.write(f"API time: {api\_time:.2f}s")

**Optimization Tips**:

1. **Cache parsed logs** \- Don't reparse on every query  
2. **Limit regex operations** \- Compile patterns once  
3. **Use generators** \- For large log files  
4. **Batch processing** \- Process logs in chunks  
5. **Async API calls** \- For multiple requests

---

## **9\. Extension Points**

### **9.1 Adding New Log Patterns**

**Example: Add Docker container ID**:

python  
*\# In config.py*  
LOG\_PATTERNS \= {  
    *\# ... existing patterns*  
    'container\_id': r'container\[\_-\]?id\[=:\\s\]+(\[a-zA-Z0-9\]+)',  
}

*\# In log\_processor.py*  
def \_extract\_identifiers(self, line: str) \-\> Dict\[str, str\]:  
    identifiers \= {}  
      
    for key in \['user\_id', 'username', 'email', 'container\_id'\]:  *\# Add here*  
        match \= re.search(self.patterns\[key\], line, re.IGNORECASE)  
        if match:  
            identifiers\[key\] \= match.group(1)  
    

    return identifiers

### **9.2 Adding New AI Models**

**Example: Add GPT-4 support**:

python  
*\# In perplexity\_agent.py*  
class AIAgent:  
    def \_\_init\_\_(self, provider: str, api\_key: str):  
        self.provider \= provider  
          
        if provider \== 'perplexity':  
            self.base\_url \= "https://api.perplexity.ai/chat/completions"  
        elif provider \== 'openai':  
            self.base\_url \= "https://api.openai.com/v1/chat/completions"  
          
    def \_get\_model(self, depth: str) \-\> str:  
        if self.provider \== 'perplexity':  
            return self.perplexity\_models\[depth\]  
        elif self.provider \== 'openai':

            return self.openai\_models\[depth\]

### **9.3 Adding Export Functionality**

**Example: Export analysis to PDF**:

python  
*\# In main.py*  
from fpdf import FPDF

def export\_analysis():  
    pdf \= FPDF()  
    pdf.add\_page()  
    pdf.set\_font("Arial", size\=12)  
      
    for msg in st.session\_state.messages:  
        pdf.cell(200, 10, txt\=f"{msg\['role'\]}: {msg\['content'\]}", ln\=True)  
      
    pdf\_output \= pdf.output(dest\='S').encode('latin-1')  
    return pdf\_output

if st.button("Export to PDF"):  
    pdf\_bytes \= export\_analysis()  
    st.download\_button(  
        label\="Download PDF",  
        data\=pdf\_bytes,  
        file\_name\="log\_analysis.pdf",  
        mime\="application/pdf"

    )

### **9.4 Adding Real-time Log Streaming**

**Example: Monitor log file changes**:

python  
import watchdog  
from watchdog.observers import Observer  
from watchdog.events import FileSystemEventHandler

class LogFileHandler(FileSystemEventHandler):  
    def on\_modified(self, event):  
        if event.src\_path.endswith('.log'):  
            *\# Read new lines*  
            with open(event.src\_path, 'r') as f:  
                new\_lines \= f.readlines()  
              
            *\# Process new logs*  
            processor.parse\_logs('\\n'.join(new\_lines))  
              
            *\# Update UI*  
            st.rerun()

*\# Start watching*  
observer \= Observer()  
observer.schedule(LogFileHandler(), path\='/var/log', recursive\=False)

observer.start()

### **9.5 Adding Database Storage**

**Example: Store analysis history**:

python  
import sqlite3

*\# Create database*  
conn \= sqlite3.connect('log\_analysis.db')  
cursor \= conn.cursor()

cursor.execute('''  
CREATE TABLE IF NOT EXISTS analysis\_history (  
    id INTEGER PRIMARY KEY,  
    timestamp TEXT,  
    query TEXT,  
    response TEXT,  
    log\_file TEXT  
)  
''')

*\# Save analysis*  
def save\_analysis(query, response, log\_file):  
    cursor.execute(  
        'INSERT INTO analysis\_history (timestamp, query, response, log\_file) VALUES (?, ?, ?, ?)',  
        (datetime.now().isoformat(), query, response, log\_file)  
    )  
    conn.commit()

*\# Retrieve history*  
def get\_history(limit\=10):  
    cursor.execute(  
        'SELECT \* FROM analysis\_history ORDER BY timestamp DESC LIMIT ?',  
        (limit,)  
    )

    return cursor.fetchall()

### **9.6 Adding Multi-file Support**

**Example: Analyze multiple log files**:

python  
*\# In main.py*  
uploaded\_files \= st.file\_uploader(  
    "Choose log files",  
    type\=\['log', 'txt', 'json'\],  
    accept\_multiple\_files\=True  
)

if uploaded\_files:  
    all\_logs \= \[\]  
      
    for uploaded\_file in uploaded\_files:  
        content \= uploaded\_file.read().decode('utf-8')  
        logs \= processor.parse\_logs(content)  
          
        *\# Add source file to each log*  
        for log in logs:  
            log\['source\_file'\] \= uploaded\_file.name  
          
        all\_logs.extend(logs)  
      
    st.session\_state.log\_data \= all\_logs

    st.success(f"Processed {len(all\_logs)} logs from {len(uploaded\_files)} files")

### **9.7 Adding Alert System**

**Example: Email alerts for critical errors**:

python  
import smtplib  
from email.mime.text import MIMEText

def send\_alert(error\_details):  
    msg \= MIMEText(f"Critical error detected:\\n\\n{error\_details}")  
    msg\['Subject'\] \= 'Log Analysis Alert'  
    msg\['From'\] \= 'alerts@yourcompany.com'  
    msg\['To'\] \= 'team@yourcompany.com'  
      
    with smtplib.SMTP('smtp.gmail.com', 587) as server:  
        server.starttls()  
        server.login('your\_email', 'your\_password')  
        server.send\_message(msg)

*\# Check for critical patterns*  
def check\_critical\_errors(logs):  
    critical\_count \= len(\[l for l in logs if l\['level'\] \== 'FATAL'\])  
      
    if critical\_count \> 10:

        send\_alert(f"Found {critical\_count} fatal errors in last hour")

---

## **10\. Best Practices for Team**

### **10.1 Code Maintenance**

1. **Regular Updates**:  
   * Update dependencies monthly  
   * Check for Perplexity API changes  
   * Review and update regex patterns  
2. **Documentation**:  
   * Comment complex regex patterns  
   * Document new features  
   * Update this KT document  
3. **Version Control**:  
   * Use meaningful commit messages  
   * Branch for new features  
   * Code reviews before merging

### **10.2 Deployment Checklist**

*  Python 3.11 or 3.12 installed  
*  Virtual environment created  
*  Dependencies installed  
*  API key configured  
*  Test with sample logs  
*  Performance testing  
*  Error handling verified  
*  Documentation updated  
*  Team training completed

### **10.3 Security Considerations**

1. **API Key Protection**:  
   * Never commit API keys to git  
   * Use environment variables  
   * Rotate keys periodically  
2. **Log Data Privacy**:  
   * Sanitize sensitive information  
   * Don't log passwords or tokens  
   * GDPR compliance if applicable  
3. **Access Control**:  
   * Limit who can access the tool  
   * Audit log analysis requests  
   * Monitor API usage

### **10.4 Monitoring & Alerts**

**What to Monitor**:

* API response times  
* Error rates  
* User activity  
* Log processing times  
* API costs

**Set Alerts For**:

* API failures  
* High error rates in logs  
* Unusual patterns  
* Performance degradation

---

## **11\. Glossary**

**Terms Used**:

* **Session State**: Streamlit's way to persist data between reruns  
* **Regex**: Regular Expression \- pattern matching for text  
* **API**: Application Programming Interface  
* **LLM**: Large Language Model (AI)  
* **Context**: Information sent to AI for analysis  
* **Token**: Unit of text for AI models (roughly 4 characters)  
* **Endpoint**: API URL or specific function/route  
* **Trace ID**: Unique identifier for request tracking  
* **Journey**: Complete sequence of user actions  
* **Pattern**: Recurring error or behavior

---

## **12\. FAQ for Team**

**Q: How much does it cost to run?** A: Depends on Perplexity API usage. Monitor via their dashboard.

**Q: Can we use OpenAI instead?** A: Yes\! See Extension Points section for adding new providers.

**Q: What's the maximum log file size?** A: Currently 10MB. Can be increased in config.py.

**Q: How accurate is the AI analysis?** A: Very accurate for pattern detection. Always verify critical findings.

**Q: Can we run this in production?** A: Yes, but add authentication and monitoring first.

**Q: What if Perplexity API is down?** A: Implement fallback to basic regex analysis without AI.

**Q: How do we add support for JSON logs?** A: Add JSON parsing in `parse_logs()` method.

---

## **13\. Contact & Support**

**For Questions Contact**:

* Technical Lead: Abhijit(abhijit201@gmail.com)  
* DevOps Team: Abhijit(abhijit201@gmail.com)  
* Documentation: This file \+ code comments

**Resources**:

* Perplexity API Docs: [https://docs.perplexity.ai](https://docs.perplexity.ai/)  
* Streamlit Docs: [https://docs.streamlit.io](https://docs.streamlit.io/)  
* Python Regex: [https://docs.python.org/3/library/re.html](https://docs.python.org/3/library/re.html)

---

**Document Version**: 1.0  
**Last Updated**: October 30, 2024  
**Maintained By**: Development Team

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>