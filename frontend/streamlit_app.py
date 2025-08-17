import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import asyncio

from components.dashboard import render_dashboard
from components.evolution_monitor import render_evolution_monitor
from components.agent_controller import render_agent_controller

# Configuration
API_BASE_URL = "http://backend:8000"  # Docker service name
# API_BASE_URL = "http://localhost:8000"  # For local development

st.set_page_config(
    page_title="SEAA Business Intelligence Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        padding: 1rem 0;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .evolution-card {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Self-Evolving Agent Architecture</h1>
        <p>Enterprise Business Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Agent Controller", "Evolution Monitor", "Analytics", "Settings"]
    )
    
    # Initialize session state
    if 'agents' not in st.session_state:
        st.session_state.agents = []
    if 'selected_agent' not in st.session_state:
        st.session_state.selected_agent = None
    
    # Load agents
    try:
        response = requests.get(f"{API_BASE_URL}/agents")
        if response.status_code == 200:
            st.session_state.agents = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to backend: {str(e)}")
        return
    
    # Render selected page
    if page == "Dashboard":
        render_dashboard(st.session_state.agents, API_BASE_URL)
    elif page == "Agent Controller":
        render_agent_controller(st.session_state.agents, API_BASE_URL)
    elif page == "Evolution Monitor":
        render_evolution_monitor(st.session_state.agents, API_BASE_URL)
    elif page == "Analytics":
        render_analytics_page(st.session_state.agents)
    elif page == "Settings":
        render_settings_page()

def render_analytics_page(agents):
    """Render analytics and insights page"""
    st.header("📊 Analytics & Insights")
    
    if not agents:
        st.warning("No agents available for analysis")
        return
    
    # Performance Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Performance Metrics")
        
        # Create performance comparison chart
        agent_names = [agent['name'] for agent in agents]
        metrics_data = []
        
        for agent in agents:
            for metric, value in agent['performance_metrics'].items():
                metrics_data.append({
                    'Agent': agent['name'],
                    'Metric': metric.replace('_', ' ').title(),
                    'Value': value
                })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            fig = px.bar(df, x='Agent', y='Value', color='Metric',
                        title="Performance Metrics Comparison",
                        height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Evolution History")
        
        # Evolution timeline
        evolution_data = []
        for agent in agents:
            for i, event in enumerate(agent.get('evolution_history', [])):
                evolution_data.append({
                    'Agent': agent['name'],
                    'Evolution': i + 1,
                    'Success': event.get('success', False),
                    'Timestamp': event.get('timestamp', datetime.now().isoformat())
                })
        
        if evolution_data:
            df = pd.DataFrame(evolution_data)
            fig = px.scatter(df, x='Evolution', y='Agent', 
                           color='Success', size=[1]*len(df),
                           title="Evolution Success Timeline",
                           height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Analytics
    st.subheader("Detailed Agent Analysis")
    
    if agents:
        selected_agent = st.selectbox("Select Agent for Analysis", 
                                     [agent['name'] for agent in agents])
        
        agent_data = next((a for a in agents if a['name'] == selected_agent), None)
        
        if agent_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Version", agent_data['version'])
            with col2:
                st.metric("Capabilities", len(agent_data['capabilities']))
            with col3:
                st.metric("Memory Size", f"{agent_data['memory_size']:,}")
            with col4:
                st.metric("Tool Count", agent_data['tool_count'])
            
            # Capabilities breakdown
            st.subheader("Capabilities")
            capabilities_df = pd.DataFrame({
                'Capability': agent_data['capabilities'],
                'Status': ['Active'] * len(agent_data['capabilities'])
            })
            st.dataframe(capabilities_df, use_container_width=True)

def render_settings_page():
    """Render settings and configuration page"""
    st.header("⚙️ Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolution Settings")
        
        auto_evolution = st.checkbox("Enable Automatic Evolution", value=True)
        evolution_frequency = st.slider("Evolution Frequency (hours)", 1, 24, 6)
        performance_threshold = st.slider("Performance Threshold", 0.5, 1.0, 0.8, 0.05)
        
        st.subheader("System Settings")
        max_agents = st.number_input("Maximum Agents", min_value=1, max_value=10, value=5)
        log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
    
    with col2:
        st.subheader("Notification Settings")
        
        email_notifications = st.checkbox("Email Notifications", value=True)
        evolution_alerts = st.checkbox("Evolution Alerts", value=True)
        performance_alerts = st.checkbox("Performance Alerts", value=True)
        
        st.subheader("Security Settings")
        api_authentication = st.checkbox("API Authentication", value=True)
        audit_logging = st.checkbox("Audit Logging", value=True)
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")
        
        # Here you would typically send the settings to the backend
        settings = {
            "auto_evolution": auto_evolution,
            "evolution_frequency": evolution_frequency,
            "performance_threshold": performance_threshold,
            "max_agents": max_agents,
            "log_level": log_level,
            "email_notifications": email_notifications,
            "evolution_alerts": evolution_alerts,
            "performance_alerts": performance_alerts,
            "api_authentication": api_authentication,
            "audit_logging": audit_logging
        }
        
        # Save to session state for demo purposes
        st.session_state.settings = settings

if __name__ == "__main__":
    main() 