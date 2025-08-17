import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import json

def render_dashboard(agents, api_base_url):
    """Render the main dashboard"""
    
    st.header("🏢 Business Intelligence Dashboard")
    
    if not agents:
        st.warning("No agents currently active. Please check the backend connection.")
        return
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Active Agents</h3>
            <h1>{}</h1>
        </div>
        """.format(len(agents)), unsafe_allow_html=True)
    
    with col2:
        total_capabilities = sum(len(agent['capabilities']) for agent in agents)
        st.markdown("""
        <div class="metric-card">
            <h3>Total Capabilities</h3>
            <h1>{}</h1>
        </div>
        """.format(total_capabilities), unsafe_allow_html=True)
    
    with col3:
        avg_performance = sum(
            sum(agent['performance_metrics'].values()) / len(agent['performance_metrics'])
            for agent in agents
        ) / len(agents) if agents else 0
        st.markdown("""
        <div class="metric-card">
            <h3>Avg Performance</h3>
            <h1>{:.1%}</h1>
        </div>
        """.format(avg_performance), unsafe_allow_html=True)
    
    with col4:
        total_evolutions = sum(len(agent.get('evolution_history', [])) for agent in agents)
        st.markdown("""
        <div class="metric-card">
            <h3>Total Evolutions</h3>
            <h1>{}</h1>
        </div>
        """.format(total_evolutions), unsafe_allow_html=True)
    
    # Real-time Monitoring
    st.subheader("📈 Real-time Performance Monitoring")
    
    # Create performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Agent performance comparison
        agent_perf_data = []
        for agent in agents:
            avg_perf = sum(agent['performance_metrics'].values()) / len(agent['performance_metrics'])
            agent_perf_data.append({
                'Agent': agent['name'],
                'Performance': avg_perf,
                'Version': agent['version']
            })
        
        df_perf = pd.DataFrame(agent_perf_data)
        fig_perf = px.bar(df_perf, x='Agent', y='Performance',
                         title="Agent Performance Comparison",
                         color='Performance',
                         color_continuous_scale='Viridis')
        fig_perf.update_layout(height=400)
        st.plotly_chart(fig_perf, use_container_width=True)
    
    with col2:
        # Capability distribution
        capability_counts = {}
        for agent in agents:
            for capability in agent['capabilities']:
                capability_counts[capability] = capability_counts.get(capability, 0) + 1
        
        if capability_counts:
            df_cap = pd.DataFrame(list(capability_counts.items()), 
                                 columns=['Capability', 'Count'])
            fig_cap = px.pie(df_cap, values='Count', names='Capability',
                           title="Capability Distribution")
            fig_cap.update_layout(height=400)
            st.plotly_chart(fig_cap, use_container_width=True)
    
    # Agent Status Table
    st.subheader("🤖 Agent Status Overview")
    
    status_data = []
    for agent in agents:
        status_data.append({
            'Name': agent['name'],
            'Version': agent['version'],
            'Status': '🟢 Active' if agent.get('active', True) else '🔴 Inactive',
            'Last Evolution': agent.get('last_evolution', 'Never'),
            'Performance': f"{sum(agent['performance_metrics'].values()) / len(agent['performance_metrics']):.1%}",
            'Capabilities': len(agent['capabilities'])
        })
    
    status_df = pd.DataFrame(status_data)
    st.dataframe(status_df, use_container_width=True)
    
    # Recent Evolution Activity
    st.subheader("🔄 Recent Evolution Activity")
    
    recent_evolutions = []
    for agent in agents:
        for evolution in agent.get('evolution_history', [])[-5:]:  # Last 5 evolutions
            recent_evolutions.append({
                'Agent': agent['name'],
                'Timestamp': evolution.get('timestamp', 'Unknown'),
                'Trigger': evolution.get('trigger', 'Unknown'),
                'Success': '✅' if evolution.get('success', False) else '❌',
                'Changes': len(evolution.get('changes', {}))
            })
    
    if recent_evolutions:
        evolution_df = pd.DataFrame(recent_evolutions)
        st.dataframe(evolution_df, use_container_width=True)
    else:
        st.info("No recent evolution activity")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Trigger Evolution", type="primary"):
            trigger_evolution_for_all_agents(agents, api_base_url)
    
    with col2:
        if st.button("📊 Generate Report"):
            generate_business_report(agents)
    
    with col3:
        if st.button("🔍 Run Diagnostics"):
            run_system_diagnostics(agents, api_base_url)
    
    with col4:
        if st.button("💾 Export Data"):
            export_agent_data(agents)

def trigger_evolution_for_all_agents(agents, api_base_url):
    """Trigger evolution for all active agents"""
    with st.spinner("Triggering evolution for all agents..."):
        success_count = 0
        for agent in agents:
            try:
                response = requests.post(
                    f"{api_base_url}/agents/{agent['agent_id']}/evolve",
                    json={
                        "trigger": "user_feedback",
                        "evolution_type": "incremental",
                        "feedback": "Dashboard triggered evolution"
                    }
                )
                if response.status_code == 200:
                    success_count += 1
            except Exception as e:
                st.error(f"Failed to trigger evolution for {agent['name']}: {str(e)}")
        
        if success_count > 0:
            st.success(f"Evolution triggered for {success_count} agents")
        else:
            st.error("Failed to trigger evolution for any agents")

def generate_business_report(agents):
    """Generate a comprehensive business report"""
    st.info("Generating comprehensive business intelligence report...")
    
    # Create a detailed report
    report_data = {
        "generated_at": datetime.now().isoformat(),
        "total_agents": len(agents),
        "agent_summary": []
    }
    
    for agent in agents:
        agent_summary = {
            "name": agent['name'],
            "performance": sum(agent['performance_metrics'].values()) / len(agent['performance_metrics']),
            "capabilities": len(agent['capabilities']),
            "evolution_count": len(agent.get('evolution_history', []))
        }
        report_data["agent_summary"].append(agent_summary)
    
    # Display report
    st.json(report_data)
    st.success("Business report generated successfully!")

def run_system_diagnostics(agents, api_base_url):
    """Run comprehensive system diagnostics"""
    with st.spinner("Running system diagnostics..."):
        diagnostics = {
            "system_health": "Healthy",
            "agent_count": len(agents),
            "avg_performance": sum(
                sum(agent['performance_metrics'].values()) / len(agent['performance_metrics'])
                for agent in agents
            ) / len(agents) if agents else 0,
            "issues_detected": []
        }
        
        # Check for performance issues
        for agent in agents:
            avg_perf = sum(agent['performance_metrics'].values()) / len(agent['performance_metrics'])
            if avg_perf < 0.7:
                diagnostics["issues_detected"].append(f"Low performance detected in {agent['name']}")
        
        # Display diagnostics
        if diagnostics["issues_detected"]:
            st.warning("Issues detected:")
            for issue in diagnostics["issues_detected"]:
                st.write(f"⚠️ {issue}")
        else:
            st.success("System diagnostics completed. No issues detected.")

def export_agent_data(agents):
    """Export agent data to downloadable format"""
    if not agents:
        st.warning("No agent data to export")
        return
    
    # Convert to DataFrame for export
    export_data = []
    for agent in agents:
        export_data.append({
            'Agent Name': agent['name'],
            'Version': agent['version'],
            'Active': agent.get('active', True),
            'Capabilities': ', '.join(agent['capabilities']),
            'Average Performance': sum(agent['performance_metrics'].values()) / len(agent['performance_metrics']),
            'Evolution Count': len(agent.get('evolution_history', [])),
            'Memory Size': agent.get('memory_size', 0),
            'Tool Count': agent.get('tool_count', 0)
        })
    
    df = pd.DataFrame(export_data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="Download Agent Data CSV",
        data=csv,
        file_name=f"seaa_agent_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    ) 