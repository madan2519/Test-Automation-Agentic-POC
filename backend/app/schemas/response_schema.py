from pydantic import BaseModel
from typing import List, Optional

class TestCaseResult(BaseModel):
    name: str
    status: str  # "passed", "failed", "error", "skipped"
    duration: str
    error_message: str = ""

class ExecutionResult(BaseModel):
    tests_run: int
    passed: int
    failed: int
    execution_time: str
    test_cases: List[TestCaseResult] = []
    logs: str

class AgentResponse(BaseModel):
    agent_name: str
    status: str
    message: str
    data: Optional[dict] = None
