from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    RESEARCH = "research"
    ESSAY = "essay"
    QUIZ = "quiz"
    CODING = "coding"
    VERIFIER = "verifier"

class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    SELF_CORRECTING = "self_correcting"
    COMPLETED = "completed"
    FAILED = "failed"

class SubTask(BaseModel):
    id: str
    target_agent: AgentRole
    description: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    is_completed: bool = False
    error: Optional[str] = None

class ExecutionPlan(BaseModel):
    task_goal: str
    subtasks: List[SubTask] = Field(default_factory=list)
    requires_parallel: bool = False

class VerificationResult(BaseModel):
    is_passed: bool
    score: float = 1.0
    critique: Optional[str] = None
    suggested_fix: Optional[str] = None

class AgentWorkflowState(BaseModel):
    session_id: str
    user_input: str
    plan: Optional[ExecutionPlan] = None
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)
    verification: Optional[VerificationResult] = None
    final_output: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = 0
    max_retries: int = 2
    execution_logs: List[str] = Field(default_factory=list)

    def log(self, message: str) -> None:
        self.execution_logs.append(message)
