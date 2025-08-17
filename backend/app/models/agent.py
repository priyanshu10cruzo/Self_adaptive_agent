from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class EvolutionTrigger(str, Enum):
    PERFORMANCE_THRESHOLD = "performance_threshold"
    TASK_FAILURE = "task_failure"
    USER_FEEDBACK = "user_feedback"
    SCHEDULED = "scheduled"

class AgentCapability(str, Enum):
    DATA_ANALYSIS = "data_analysis"
    REPORT_GENERATION = "report_generation"
    TASK_AUTOMATION = "task_automation"
    PREDICTIVE_MODELING = "predictive_modeling"
    NATURAL_LANGUAGE_PROCESSING = "natural_language_processing"

class EvolutionEvent(BaseModel):
    timestamp: datetime
    trigger: EvolutionTrigger
    changes: Dict[str, Any]
    performance_before: Dict[str, float]
    performance_after: Dict[str, float]
    success: bool
    notes: Optional[str] = None

class AgentState(BaseModel):
    agent_id: str
    name: str
    version: str
    capabilities: List[str]
    performance_metrics: Dict[str, float]
    evolution_history: List[EvolutionEvent]
    created_at: datetime
    last_evolution: datetime
    active: bool = True
    memory_size: int = 1000
    tool_count: int = 0

class EvolutionRequest(BaseModel):
    trigger: EvolutionTrigger
    target_metrics: Optional[Dict[str, float]] = None
    feedback: Optional[str] = None
    evolution_type: str = "incremental"  # incremental, major, architectural

class TaskRequest(BaseModel):
    task_type: str
    parameters: Dict[str, Any]
    priority: int = Field(default=1, ge=1, le=5)
    timeout: Optional[int] = 300 