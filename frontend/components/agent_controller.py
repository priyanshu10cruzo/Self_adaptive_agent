import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import json

def render_agent_controller(agents, api_base_url):
    """Render the agent controller page"""
    
    st.header("🎮 Agent Controller")
    
    if not agents:
        st.warning("No agents available for control")
        return
    
    # Agent Selection
    st.subheader("🤖 Agent Selection")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_agent_name = st.selectbox("Select Agent", [agent['name'] for agent in agents])
    
    with col2:
        if st.button("🔄 Refresh Agent List"):
            st.rerun()
    
    selected_agent = next((a for a in agents if a['name'] == selected_agent_name), None)
    
    if not selected_agent:
        st.error("Selected agent not found")
        return
    
    # Agent Information
    st.subheader("📋 Agent Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Agent ID", selected_agent['agent_id'])
        st.metric("Version", selected_agent['version'])
    
    with col2:
        st.metric("Status", "🟢 Active" if selected_agent.get('active', True) else "🔴 Inactive")
        st.metric("Memory Size", f"{selected_agent.get('memory_size', 0):,}")
    
    with col3:
        st.metric("Tool Count", selected_agent.get('tool_count', 0))
        st.metric("Capabilities", len(selected_agent['capabilities']))
    
    with col4:
        avg_performance = sum(selected_agent['performance_metrics'].values()) / len(selected_agent['performance_metrics'])
        st.metric("Avg Performance", f"{avg_performance:.1%}")
        st.metric("Evolutions", len(selected_agent.get('evolution_history', [])))
    
    # Performance Metrics
    st.subheader("📊 Performance Metrics")
    
    # Create performance radar chart
    metrics = list(selected_agent['performance_metrics'].keys())
    values = list(selected_agent['performance_metrics'].values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name='Current Performance',
        line_color='#667eea'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Performance Metrics Radar Chart",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Capabilities
    st.subheader("🛠️ Capabilities")
    
    capabilities_df = pd.DataFrame({
        'Capability': selected_agent['capabilities'],
        'Status': ['Active'] * len(selected_agent['capabilities']),
        'Category': ['Business Intelligence'] * len(selected_agent['capabilities'])
    })
    
    st.dataframe(capabilities_df, use_container_width=True)
    
    # Task Execution
    st.subheader("⚡ Task Execution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        task_type = st.selectbox("Task Type", [
            "data_analysis",
            "report_generation", 
            "task_automation",
            "predictive_modeling",
            "custom"
        ])
        
        if task_type == "custom":
            custom_task = st.text_input("Custom Task Type", placeholder="Enter custom task type")
            task_type = custom_task if custom_task else task_type
        
        # Task-specific parameters
        if task_type == "data_analysis":
            analysis_type = st.selectbox("Analysis Type", ["summary", "trends", "anomalies"])
            data_source = st.text_input("Data Source", placeholder="Enter data source")
            parameters = {
                "analysis_type": analysis_type,
                "data_source": data_source
            }
        elif task_type == "report_generation":
            report_type = st.selectbox("Report Type", ["performance", "financial", "operational"])
            format_type = st.selectbox("Format", ["pdf", "html", "excel"])
            parameters = {
                "report_type": report_type,
                "format": format_type
            }
        elif task_type == "task_automation":
            automation_type = st.selectbox("Automation Type", ["data_processing", "email", "file_management"])
            schedule = st.selectbox("Schedule", ["immediate", "daily", "weekly"])
            parameters = {
                "task_type": automation_type,
                "schedule": schedule
            }
        elif task_type == "predictive_modeling":
            model_type = st.selectbox("Model Type", ["regression", "classification", "time_series"])
            data_size = st.number_input("Data Size", min_value=100, value=1000, step=100)
            parameters = {
                "model_type": model_type,
                "data_size": data_size
            }
        else:
            parameters = {}
    
    with col2:
        priority = st.slider("Priority", 1, 5, 3)
        timeout = st.number_input("Timeout (seconds)", min_value=30, value=300, step=30)
        
        if st.button("🚀 Execute Task", type="primary"):
            execute_task(selected_agent, task_type, parameters, priority, timeout, api_base_url)
    
    # Agent Control Actions
    st.subheader("🎛️ Agent Control")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Restart Agent"):
            restart_agent(selected_agent, api_base_url)
    
    with col2:
        if st.button("⏸️ Pause Agent"):
            pause_agent(selected_agent, api_base_url)
    
    with col3:
        if st.button("▶️ Resume Agent"):
            resume_agent(selected_agent, api_base_url)
    
    # Memory Management
    st.subheader("🧠 Memory Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        memory_query = st.text_input("Search Memories", placeholder="Enter search query...")
        if st.button("🔍 Search"):
            search_memories(selected_agent, memory_query, api_base_url)
    
    with col2:
        memory_data = st.text_area("Store Memory", placeholder="Enter memory data (JSON format)...")
        if st.button("💾 Store"):
            store_memory(selected_agent, memory_data, api_base_url)
    
    # Tool Management
    st.subheader("🔧 Tool Management")
    
    try:
        response = requests.get(f"{api_base_url}/agents/{selected_agent['agent_id']}/tools")
        if response.status_code == 200:
            tools_data = response.json()
            available_tools = tools_data.get('tools', [])
            
            if available_tools:
                st.write("**Available Tools:**")
                for tool in available_tools:
                    st.write(f"• {tool}")
                
                # Tool execution
                selected_tool = st.selectbox("Select Tool to Execute", available_tools)
                tool_params = st.text_area("Tool Parameters (JSON)", placeholder='{"param1": "value1"}')
                
                if st.button("🛠️ Execute Tool"):
                    execute_tool(selected_agent, selected_tool, tool_params, api_base_url)
            else:
                st.info("No tools available for this agent")
    except Exception as e:
        st.error(f"Failed to load tools: {str(e)}")
    
    # Agent History
    st.subheader("📜 Agent History")
    
    # Evolution history
    if selected_agent.get('evolution_history'):
        st.write("**Recent Evolution Events:**")
        for i, event in enumerate(selected_agent['evolution_history'][-5:]):  # Last 5 events
            with st.expander(f"Evolution {i+1} - {event.get('trigger', 'Unknown')}"):
                st.write(f"**Timestamp:** {event.get('timestamp', 'Unknown')}")
                st.write(f"**Success:** {'✅' if event.get('success', False) else '❌'}")
                st.write(f"**Changes:** {len(event.get('changes', {}))}")
                if event.get('notes'):
                    st.write(f"**Notes:** {event['notes']}")
    else:
        st.info("No evolution history available")

def execute_task(agent, task_type, parameters, priority, timeout, api_base_url):
    """Execute a task using the selected agent"""
    with st.spinner(f"Executing {task_type} task..."):
        try:
            task_request = {
                "task_type": task_type,
                "parameters": parameters,
                "priority": priority,
                "timeout": timeout
            }
            
            response = requests.post(
                f"{api_base_url}/agents/{agent['agent_id']}/execute",
                json=task_request
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"Task executed successfully!")
                
                # Display results
                with st.expander("Task Results"):
                    st.json(result)
            else:
                st.error(f"Task execution failed: {response.status_code}")
                
        except Exception as e:
            st.error(f"Error executing task: {str(e)}")

def restart_agent(agent, api_base_url):
    """Restart the selected agent"""
    st.info(f"Restart functionality for {agent['name']} would be implemented here")
    # In a real implementation, this would call a restart endpoint

def pause_agent(agent, api_base_url):
    """Pause the selected agent"""
    st.info(f"Pause functionality for {agent['name']} would be implemented here")
    # In a real implementation, this would call a pause endpoint

def resume_agent(agent, api_base_url):
    """Resume the selected agent"""
    st.info(f"Resume functionality for {agent['name']} would be implemented here")
    # In a real implementation, this would call a resume endpoint

def search_memories(agent, query, api_base_url):
    """Search agent memories"""
    if not query.strip():
        st.warning("Please enter a search query")
        return
    
    with st.spinner("Searching memories..."):
        try:
            response = requests.get(
                f"{api_base_url}/agents/{agent['agent_id']}/memory/search",
                params={"query": query, "limit": 10}
            )
            
            if response.status_code == 200:
                results = response.json()
                st.success(f"Found {results['total_results']} memory results")
                
                if results['results']:
                    for result in results['results']:
                        with st.expander(f"Memory {result['id']} - {result['timestamp']}"):
                            st.json(result['data'])
                else:
                    st.info("No memories found for this query")
            else:
                st.error(f"Memory search failed: {response.status_code}")
                
        except Exception as e:
            st.error(f"Error searching memories: {str(e)}")

def store_memory(agent, memory_data, api_base_url):
    """Store a new memory for the agent"""
    if not memory_data.strip():
        st.warning("Please enter memory data")
        return
    
    try:
        # Parse JSON data
        memory_json = json.loads(memory_data)
        
        with st.spinner("Storing memory..."):
            response = requests.post(
                f"{api_base_url}/agents/{agent['agent_id']}/memory/store",
                json=memory_json
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"Memory stored successfully! ID: {result['memory_id']}")
            else:
                st.error(f"Failed to store memory: {response.status_code}")
                
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please enter valid JSON data.")
    except Exception as e:
        st.error(f"Error storing memory: {str(e)}")

def execute_tool(agent, tool_name, tool_params, api_base_url):
    """Execute a tool for the agent"""
    if not tool_params.strip():
        st.warning("Please enter tool parameters")
        return
    
    try:
        # Parse JSON parameters
        params_json = json.loads(tool_params)
        
        with st.spinner(f"Executing tool {tool_name}..."):
            response = requests.post(
                f"{api_base_url}/agents/{agent['agent_id']}/tools/{tool_name}/execute",
                json=params_json
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"Tool {tool_name} executed successfully!")
                
                # Display results
                with st.expander("Tool Execution Results"):
                    st.json(result)
            else:
                st.error(f"Tool execution failed: {response.status_code}")
                
    except json.JSONDecodeError:
        st.error("Invalid JSON format. Please enter valid JSON data.")
    except Exception as e:
        st.error(f"Error executing tool: {str(e)}")

def get_agent_status(agent):
    """Get current status of an agent"""
    status = {
        "active": agent.get('active', True),
        "performance": sum(agent['performance_metrics'].values()) / len(agent['performance_metrics']),
        "capabilities": len(agent['capabilities']),
        "tools": agent.get('tool_count', 0),
        "memory": agent.get('memory_size', 0),
        "evolutions": len(agent.get('evolution_history', []))
    }
    
    return status 