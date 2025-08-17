from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.models.agent import AgentState, EvolutionRequest, TaskRequest
from app.core.evolution_engine import EvolutionEngine
from app.core.memory_manager import MemoryManager
from app.core.tool_manager import ToolManager

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (these would typically be injected via dependency injection)
evolution_engine = EvolutionEngine()
memory_manager = MemoryManager()
tool_manager = ToolManager()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "evolution_engine": "active",
            "memory_manager": "active",
            "tool_manager": "active"
        }
    }

@router.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    return {
        "system_status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "uptime": "24h 15m 30s",  # This would be calculated dynamically
        "active_agents": 1,  # This would be dynamic
        "total_evolutions": 0,  # This would be dynamic
        "system_health": "excellent"
    }

@router.get("/agents/{agent_id}/memory")
async def get_agent_memory(agent_id: str):
    """Get memory statistics for an agent"""
    try:
        memory_stats = await memory_manager.get_memory_stats(agent_id)
        return {
            "agent_id": agent_id,
            "memory_stats": memory_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get memory stats for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve memory statistics")

@router.get("/agents/{agent_id}/tools")
async def get_agent_tools(agent_id: str):
    """Get tools available to an agent"""
    try:
        tools = await tool_manager.get_agent_tools(agent_id)
        tool_stats = await tool_manager.get_agent_tool_stats(agent_id)
        
        return {
            "agent_id": agent_id,
            "tools": [tool.name for tool in tools],
            "tool_stats": tool_stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get tools for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tool information")

@router.post("/agents/{agent_id}/tools/{tool_name}/execute")
async def execute_tool(agent_id: str, tool_name: str, parameters: Dict[str, Any]):
    """Execute a specific tool for an agent"""
    try:
        result = await tool_manager.execute_tool(tool_name, agent_id, **parameters)
        return {
            "agent_id": agent_id,
            "tool_name": tool_name,
            "result": result,
            "execution_timestamp": datetime.now().isoformat()
        }
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute tool {tool_name} for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Tool execution failed")

@router.get("/agents/{agent_id}/evolution/history")
async def get_evolution_history(agent_id: str, limit: int = 10):
    """Get evolution history for an agent"""
    try:
        # This would typically query the database
        # For now, return a placeholder response
        return {
            "agent_id": agent_id,
            "evolution_history": [],
            "total_evolutions": 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get evolution history for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve evolution history")

@router.get("/agents/{agent_id}/performance")
async def get_agent_performance(agent_id: str):
    """Get detailed performance metrics for an agent"""
    try:
        # This would typically query the database and calculate metrics
        # For now, return a placeholder response
        return {
            "agent_id": agent_id,
            "performance_metrics": {
                "overall_score": 0.82,
                "accuracy": 0.85,
                "efficiency": 0.78,
                "adaptability": 0.82
            },
            "performance_trend": "improving",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get performance for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")

@router.post("/agents/{agent_id}/memory/store")
async def store_memory(agent_id: str, memory_data: Dict[str, Any]):
    """Store a new memory for an agent"""
    try:
        memory_id = await memory_manager.store_memory(agent_id, memory_data)
        return {
            "agent_id": agent_id,
            "memory_id": memory_id,
            "status": "stored",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to store memory for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store memory")

@router.get("/agents/{agent_id}/memory/search")
async def search_memories(agent_id: str, query: str, limit: int = 10):
    """Search memories for an agent"""
    try:
        results = await memory_manager.search_memories(agent_id, query, limit)
        return {
            "agent_id": agent_id,
            "query": query,
            "results": results,
            "total_results": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to search memories for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search memories")

@router.post("/agents/{agent_id}/knowledge/update")
async def update_knowledge(agent_id: str, knowledge_update: Dict[str, Any]):
    """Update knowledge for an agent in a specific domain"""
    try:
        domain = knowledge_update.get("domain", "general")
        knowledge_data = knowledge_update.get("data", {})
        
        await memory_manager.update_knowledge(agent_id, domain, knowledge_data)
        
        return {
            "agent_id": agent_id,
            "domain": domain,
            "status": "updated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to update knowledge for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update knowledge")

@router.get("/agents/{agent_id}/knowledge/{domain}")
async def get_knowledge(agent_id: str, domain: str):
    """Get knowledge for an agent in a specific domain"""
    try:
        knowledge = await memory_manager.get_knowledge(agent_id, domain)
        return {
            "agent_id": agent_id,
            "domain": domain,
            "knowledge": knowledge,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get knowledge for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve knowledge")

@router.post("/agents/{agent_id}/patterns/learn")
async def learn_pattern(agent_id: str, pattern_data: Dict[str, Any]):
    """Learn and store a new pattern for an agent"""
    try:
        pattern_type = pattern_data.get("pattern_type", "general")
        pattern_info = pattern_data.get("pattern_info", {})
        
        await memory_manager.learn_pattern(agent_id, pattern_type, pattern_info)
        
        return {
            "agent_id": agent_id,
            "pattern_type": pattern_type,
            "status": "learned",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to learn pattern for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to learn pattern")

@router.get("/agents/{agent_id}/patterns/{pattern_type}")
async def get_patterns(agent_id: str, pattern_type: str):
    """Get learned patterns of a specific type for an agent"""
    try:
        patterns = await memory_manager.get_patterns(agent_id, pattern_type)
        return {
            "agent_id": agent_id,
            "pattern_type": pattern_type,
            "patterns": patterns,
            "total_patterns": len(patterns),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get patterns for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve patterns")

@router.get("/tools/categories")
async def get_tool_categories():
    """Get all available tool categories"""
    try:
        categories = list(tool_manager.tool_categories.keys())
        return {
            "categories": categories,
            "total_categories": len(categories),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get tool categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tool categories")

@router.get("/tools/category/{category}")
async def get_tools_by_category(category: str):
    """Get all tools in a specific category"""
    try:
        tools = await tool_manager.get_tools_by_category(category)
        return {
            "category": category,
            "tools": [tool.name for tool in tools],
            "total_tools": len(tools),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get tools for category {category}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tools")

@router.get("/tools/{tool_name}/stats")
async def get_tool_stats(tool_name: str):
    """Get statistics for a specific tool"""
    try:
        stats = await tool_manager.get_tool_stats(tool_name)
        if not stats:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        return {
            "tool_name": tool_name,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get stats for tool {tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve tool statistics")

@router.post("/system/analyze")
async def analyze_system():
    """Trigger system-wide analysis"""
    try:
        # This would typically trigger a comprehensive system analysis
        # For now, return a placeholder response
        return {
            "analysis_id": "sys_analysis_001",
            "status": "completed",
            "findings": [
                "System performance is optimal",
                "All agents are functioning normally",
                "No critical issues detected"
            ],
            "recommendations": [
                "Continue monitoring system performance",
                "Consider scheduled maintenance in 2 weeks"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to analyze system: {str(e)}")
        raise HTTPException(status_code=500, detail="System analysis failed")

@router.get("/system/metrics")
async def get_system_metrics():
    """Get system-wide metrics"""
    try:
        # This would typically collect metrics from all components
        # For now, return a placeholder response
        return {
            "system_metrics": {
                "total_agents": 1,
                "active_agents": 1,
                "total_evolutions": 0,
                "successful_evolutions": 0,
                "system_uptime": "24h 15m 30s",
                "memory_usage": "45%",
                "cpu_usage": "32%",
                "disk_usage": "28%"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics") 