from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime

from app.core.evolution_engine import EvolutionEngine
from app.core.memory_manager import MemoryManager
from app.core.tool_manager import ToolManager
from app.models.agent import AgentState, EvolutionRequest, TaskRequest
from app.api.routes import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Self-Evolving Agent Architecture API",
    description="Enterprise SEAA for business automation and intelligence",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://frontend:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
evolution_engine = EvolutionEngine()
memory_manager = MemoryManager()
tool_manager = ToolManager()

# Agent state storage
agent_states: Dict[str, AgentState] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the SEAA system on startup"""
    logger.info("Initializing Self-Evolving Agent Architecture...")
    
    # Initialize default agent
    default_agent = AgentState(
        agent_id="default",
        name="Business Intelligence Agent",
        version="1.0.0",
        capabilities=["data_analysis", "report_generation", "task_automation"],
        performance_metrics={"accuracy": 0.85, "efficiency": 0.78, "adaptability": 0.82},
        evolution_history=[],
        created_at=datetime.now(),
        last_evolution=datetime.now()
    )
    
    agent_states["default"] = default_agent
    await evolution_engine.initialize()
    logger.info("SEAA system initialized successfully")

@app.get("/")
async def root():
    return {"message": "Self-Evolving Agent Architecture API", "status": "active"}

@app.get("/agents", response_model=List[AgentState])
async def get_agents():
    """Get all active agents"""
    return list(agent_states.values())

@app.get("/agents/{agent_id}", response_model=AgentState)
async def get_agent(agent_id: str):
    """Get specific agent details"""
    if agent_id not in agent_states:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_states[agent_id]

@app.post("/agents/{agent_id}/evolve")
async def evolve_agent(agent_id: str, evolution_request: EvolutionRequest, background_tasks: BackgroundTasks):
    """Trigger agent evolution process"""
    if agent_id not in agent_states:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    background_tasks.add_task(perform_evolution, agent_id, evolution_request)
    return {"message": "Evolution process started", "agent_id": agent_id}

@app.post("/agents/{agent_id}/execute")
async def execute_task(agent_id: str, task_request: TaskRequest):
    """Execute a task using the specified agent"""
    if agent_id not in agent_states:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    result = await evolution_engine.execute_task(
        agent_states[agent_id], 
        task_request.task_type, 
        task_request.parameters
    )
    
    return {"result": result, "agent_id": agent_id, "timestamp": datetime.now()}

async def perform_evolution(agent_id: str, evolution_request: EvolutionRequest):
    """Background task for agent evolution"""
    try:
        agent = agent_states[agent_id]
        evolved_agent = await evolution_engine.evolve_agent(agent, evolution_request)
        agent_states[agent_id] = evolved_agent
        logger.info(f"Agent {agent_id} evolved successfully")
    except Exception as e:
        logger.error(f"Evolution failed for agent {agent_id}: {str(e)}")

# Include API routes
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 