"""
FastAPI dependencies
"""
from app.workflow.engine import AutonomousWorkflowEngine

_engine_instance = None

def get_engine() -> AutonomousWorkflowEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AutonomousWorkflowEngine()
    return _engine_instance
