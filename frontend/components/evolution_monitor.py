import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import json

def render_evolution_monitor(agents, api_base_url):
    """Render the evolution monitoring page"""
    
    st.header("🔄 Evolution Monitor")
    
    if not agents:
        st.warning("No agents available for monitoring")
        return
    
    # Evolution Overview
    st.subheader("📊 Evolution Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_evolutions = sum(len(agent.get('evolution_history', [])) for agent in agents)
        st.metric("Total Evolutions", total_evolutions)
    
    with col2:
        successful_evolutions = sum(
            sum(1 for event in agent.get('evolution_history', []) if event.get('success', False))
            for agent in agents
        )
        st.metric("Successful Evolutions", successful_evolutions)
    
    with col3:
        success_rate = (successful_evolutions / total_evolutions * 100) if total_evolutions > 0 else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col4:
        recent_evolutions = sum(
            sum(1 for event in agent.get('evolution_history', []) 
                if event.get('timestamp') and 
                datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')) > datetime.now() - timedelta(days=7))
            for agent in agents
        )
        st.metric("Recent Evolutions (7d)", recent_evolutions)
    
    # Evolution Timeline
    st.subheader("📈 Evolution Timeline")
    
    evolution_data = []
    for agent in agents:
        for i, event in enumerate(agent.get('evolution_history', [])):
            try:
                timestamp = datetime.fromisoformat(event.get('timestamp', datetime.now().isoformat()).replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
            
            evolution_data.append({
                'Agent': agent['name'],
                'Evolution': i + 1,
                'Timestamp': timestamp,
                'Success': event.get('success', False),
                'Trigger': event.get('trigger', 'Unknown'),
                'Changes': len(event.get('changes', {})),
                'Performance_Before': sum(event.get('performance_before', {}).values()) / len(event.get('performance_before', {})) if event.get('performance_before') else 0,
                'Performance_After': sum(event.get('performance_after', {}).values()) / len(event.get('performance_after', {})) if event.get('performance_after') else 0
            })
    
    if evolution_data:
        # Sort by timestamp
        evolution_data.sort(key=lambda x: x['Timestamp'])
        
        # Create timeline chart
        df_evolution = pd.DataFrame(evolution_data)
        
        # Performance improvement chart
        fig_performance = px.scatter(df_evolution, 
                                   x='Timestamp', 
                                   y='Performance_After',
                                   color='Agent',
                                   size='Changes',
                                   hover_data=['Evolution', 'Success', 'Trigger'],
                                   title="Performance After Evolution",
                                   height=400)
        st.plotly_chart(fig_performance, use_container_width=True)
        
        # Success rate by agent
        success_by_agent = df_evolution.groupby('Agent')['Success'].agg(['count', 'sum']).reset_index()
        success_by_agent['success_rate'] = success_by_agent['sum'] / success_by_agent['count']
        
        fig_success = px.bar(success_by_agent, 
                           x='Agent', 
                           y='success_rate',
                           title="Evolution Success Rate by Agent",
                           height=400)
        fig_success.update_yaxis(title="Success Rate")
        st.plotly_chart(fig_success, use_container_width=True)
        
        # Evolution details table
        st.subheader("📋 Evolution Details")
        
        # Prepare data for display
        display_data = []
        for event in evolution_data:
            display_data.append({
                'Agent': event['Agent'],
                'Evolution': event['Evolution'],
                'Date': event['Timestamp'].strftime('%Y-%m-%d %H:%M'),
                'Trigger': event['Trigger'],
                'Success': '✅' if event['Success'] else '❌',
                'Changes': event['Changes'],
                'Performance Before': f"{event['Performance_Before']:.3f}",
                'Performance After': f"{event['Performance_After']:.3f}",
                'Improvement': f"{(event['Performance_After'] - event['Performance_Before']):.3f}"
            })
        
        df_display = pd.DataFrame(display_data)
        st.dataframe(df_display, use_container_width=True)
        
    else:
        st.info("No evolution history available")
    
    # Trigger Evolution
    st.subheader("🚀 Trigger Evolution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_agent = st.selectbox("Select Agent", [agent['name'] for agent in agents])
        evolution_type = st.selectbox("Evolution Type", ["incremental", "major", "architectural"])
        trigger_type = st.selectbox("Trigger Type", ["user_feedback", "performance_threshold", "scheduled"])
    
    with col2:
        feedback = st.text_area("Feedback/Notes", placeholder="Enter feedback or notes for evolution...")
        
        if st.button("🔄 Trigger Evolution", type="primary"):
            trigger_evolution(selected_agent, evolution_type, trigger_type, feedback, agents, api_base_url)
    
    # Evolution Settings
    st.subheader("⚙️ Evolution Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        auto_evolution = st.checkbox("Enable Automatic Evolution", value=True)
        performance_threshold = st.slider("Performance Threshold for Auto-Evolution", 0.5, 1.0, 0.8, 0.05)
        evolution_frequency = st.slider("Maximum Evolution Frequency (hours)", 1, 168, 24)
    
    with col2:
        evolution_strategies = st.multiselect(
            "Preferred Evolution Strategies",
            ["incremental", "major", "architectural", "adaptive"],
            default=["incremental", "major"]
        )
        rollback_enabled = st.checkbox("Enable Automatic Rollback on Failure", value=True)
    
    if st.button("💾 Save Evolution Settings"):
        save_evolution_settings({
            "auto_evolution": auto_evolution,
            "performance_threshold": performance_threshold,
            "evolution_frequency": evolution_frequency,
            "evolution_strategies": evolution_strategies,
            "rollback_enabled": rollback_enabled
        })

def trigger_evolution(agent_name, evolution_type, trigger_type, feedback, agents, api_base_url):
    """Trigger evolution for a specific agent"""
    agent = next((a for a in agents if a['name'] == agent_name), None)
    
    if not agent:
        st.error("Agent not found")
        return
    
    with st.spinner(f"Triggering {evolution_type} evolution for {agent_name}..."):
        try:
            evolution_request = {
                "trigger": trigger_type,
                "evolution_type": evolution_type,
                "feedback": feedback if feedback else f"Manual evolution triggered via UI - {evolution_type} type"
            }
            
            response = requests.post(
                f"{api_base_url}/agents/{agent['agent_id']}/evolve",
                json=evolution_request
            )
            
            if response.status_code == 200:
                st.success(f"Evolution process started for {agent_name}")
                
                # Show evolution details
                st.info(f"""
                **Evolution Details:**
                - **Agent:** {agent_name}
                - **Type:** {evolution_type}
                - **Trigger:** {trigger_type}
                - **Status:** Process started
                - **Request ID:** {response.json().get('agent_id', 'N/A')}
                """)
                
                # Refresh the page to show updated data
                st.rerun()
            else:
                st.error(f"Failed to trigger evolution: {response.status_code}")
                
        except Exception as e:
            st.error(f"Error triggering evolution: {str(e)}")

def save_evolution_settings(settings):
    """Save evolution settings"""
    # In a real application, this would save to backend/database
    st.session_state.evolution_settings = settings
    st.success("Evolution settings saved successfully!")

def get_evolution_analytics(agents):
    """Get analytics for evolution patterns"""
    if not agents:
        return {}
    
    analytics = {
        "total_evolutions": 0,
        "success_rate": 0,
        "avg_performance_improvement": 0,
        "evolution_frequency": {},
        "trigger_distribution": {},
        "agent_performance": {}
    }
    
    total_evolutions = 0
    successful_evolutions = 0
    total_improvement = 0
    improvement_count = 0
    
    for agent in agents:
        agent_evolutions = agent.get('evolution_history', [])
        total_evolutions += len(agent_evolutions)
        
        for event in agent_evolutions:
            if event.get('success', False):
                successful_evolutions += 1
            
            # Calculate performance improvement
            if event.get('performance_before') and event.get('performance_after'):
                before = sum(event['performance_before'].values()) / len(event['performance_before'])
                after = sum(event['performance_after'].values()) / len(event['performance_after'])
                improvement = after - before
                total_improvement += improvement
                improvement_count += 1
            
            # Track trigger distribution
            trigger = event.get('trigger', 'unknown')
            analytics["trigger_distribution"][trigger] = analytics["trigger_distribution"].get(trigger, 0) + 1
        
        # Track agent performance
        if agent_evolutions:
            agent_success_rate = sum(1 for e in agent_evolutions if e.get('success', False)) / len(agent_evolutions)
            analytics["agent_performance"][agent['name']] = {
                "evolution_count": len(agent_evolutions),
                "success_rate": agent_success_rate,
                "current_performance": sum(agent['performance_metrics'].values()) / len(agent['performance_metrics'])
            }
    
    analytics["total_evolutions"] = total_evolutions
    analytics["success_rate"] = successful_evolutions / total_evolutions if total_evolutions > 0 else 0
    analytics["avg_performance_improvement"] = total_improvement / improvement_count if improvement_count > 0 else 0
    
    return analytics 