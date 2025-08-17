from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class EvolutionStrategy(str, Enum):
    INCREMENTAL = "incremental"
    MAJOR = "major"
    ARCHITECTURAL = "architectural"
    ADAPTIVE = "adaptive"

class EvolutionPhase(str, Enum):
    ANALYSIS = "analysis"
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"

class EvolutionMetrics(BaseModel):
    accuracy_improvement: float
    efficiency_gain: float
    adaptability_score: float
    resource_utilization: float
    overall_score: float

class EvolutionPlan(BaseModel):
    strategy: EvolutionStrategy
    phases: List[EvolutionPhase]
    estimated_duration: int  # in minutes
    resource_requirements: Dict[str, Any]
    risk_assessment: str
    success_criteria: List[str]

class EvolutionResult(BaseModel):
    success: bool
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    improvement: Dict[str, float]
    execution_time: float
    errors: List[str]
    warnings: List[str] 