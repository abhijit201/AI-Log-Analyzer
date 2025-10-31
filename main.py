import streamlit as st
import json
from datetime import datetime
from config import Config
from log_processor import LogProcessor
from perplexity_agent import PerplexityAgent

# Page config
st.set_page_config(
    page_title="AI Log Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
        .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        color: #0d47a1;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #667eea;
        color: #1a1a1a;
    }
    .stChatInput textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
    }
    .stChatInput {
        background-color: #ffffff !important;
    }
    .error-badge {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .success-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'log_data' not in st.session_state:
    st.session_state.log_data = None
if 'log_processor' not in st.session_state:
    st.session_state.log_processor = None
if 'agent' not in st.session_state:
    st.session_state.agent = None

# Header
st.markdown('<div class="main-header">🔍 AI Log Analyzer</div>', unsafe_allow_html=True)
st.markdown("**Intelligent log analysis powered by Perplexity AI**")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input(
        "Perplexity API Key",
        type="password",
        value=st.session_state.get('api_key', ''),
        help="Enter your Perplexity API key"
    )
    
    if api_key:
        st.session_state.api_key = api_key
        if not st.session_state.agent:
            st.session_state.agent = PerplexityAgent(api_key)
    
    st.divider()
    
    st.header("📊 Analysis Options")
    analysis_depth = st.select_slider(
        "Analysis Depth",
        options=["Quick", "Standard", "Deep"],
        value="Standard"
    )
    
    auto_detect_user = st.checkbox("Auto-detect user identifiers", value=True)
    
    st.divider()
    
    if st.session_state.log_data:
        st.success(f"✅ Log file loaded")
        st.info(f"📝 {len(st.session_state.log_data)} log entries")
        
        if st.button("🗑️ Clear Log Data"):
            st.session_state.log_data = None
            st.session_state.log_processor = None
            st.session_state.messages = []
            st.rerun()

# Main content area
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📁 Upload Log File")
    
    uploaded_file = st.file_uploader(
        "Choose a log file",
        type=['log', 'txt', 'json'],
        help="Upload your application log file"
    )
    
    if uploaded_file:
        try:
            # Read file content
            content = uploaded_file.read().decode('utf-8')
            
            # Process logs
            if not st.session_state.log_processor:
                st.session_state.log_processor = LogProcessor()
            
            st.session_state.log_data = st.session_state.log_processor.parse_logs(content)
            
            st.success(f"✅ Processed {len(st.session_state.log_data)} log entries")
            
            # Quick stats
            stats = st.session_state.log_processor.get_statistics()
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Errors", stats.get('errors', 0))
            with col_b:
                st.metric("Warnings", stats.get('warnings', 0))
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("💬 Chat with Your Logs")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message user-message">👤 {message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 {message["content"]}</div>', 
                          unsafe_allow_html=True)
    
    # Chat input
    if st.session_state.log_data and st.session_state.agent:
        prompt = st.chat_input("Ask about your logs... (e.g., 'Find all errors for user john123')")
        
        if prompt:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Process with agent
            with st.spinner("🔍 Analyzing logs..."):
                try:
                    response = st.session_state.agent.analyze_logs(
                        prompt,
                        st.session_state.log_data,
                        st.session_state.log_processor,
                        analysis_depth,
                        auto_detect_user
                    )
                    
                    # Add assistant response
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            st.rerun()
    
    elif not api_key:
        st.info("👈 Please enter your Perplexity API key in the sidebar")
    elif not st.session_state.log_data:
        st.info("👈 Please upload a log file to start analyzing")

# Quick action buttons
if st.session_state.log_data and st.session_state.agent:
    st.divider()
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔴 Find All Errors"):
            prompt = "Find all errors and exceptions in the logs"
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Analyzing..."):
                response = st.session_state.agent.analyze_logs(
                    prompt, st.session_state.log_data, 
                    st.session_state.log_processor, analysis_depth, auto_detect_user
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("👥 List Users"):
            prompt = "List all unique users found in the logs"
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Analyzing..."):
                response = st.session_state.agent.analyze_logs(
                    prompt, st.session_state.log_data,
                    st.session_state.log_processor, analysis_depth, auto_detect_user
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("📊 API Summary"):
            prompt = "Provide a summary of all API calls and their status"
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Analyzing..."):
                response = st.session_state.agent.analyze_logs(
                    prompt, st.session_state.log_data,
                    st.session_state.log_processor, analysis_depth, auto_detect_user
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col4:
        if st.button("🔍 Error Patterns"):
            prompt = "Identify common error patterns and their root causes"
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Analyzing..."):
                response = st.session_state.agent.analyze_logs(
                    prompt, st.session_state.log_data,
                    st.session_state.log_processor, analysis_depth, auto_detect_user
                )
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
