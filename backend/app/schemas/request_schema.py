from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Annotated
from langgraph.channels import LastValue
from schemas.response_schema import ExecutionResult
from schemas.test_plan_schema import TestPlan

class AutomationRequest(BaseModel):
    jira_id: str = Field(..., description="The Jira ticket ID (e.g., PLAT-123)")
    platform: str = Field(..., description="Target platform: Web, Mobile, API")
    language: str = Field(..., description="Programming language: Python, Java")
    framework: str = Field(..., description="Automation framework: Playwright, Selenium, Appium, Robot Framework")
    browser: Optional[str] = Field(None, description="Target browser (e.g. Chrome, Edge)")
    device: Optional[str] = Field(None, description="Target device (e.g. Pixel 5, iPhone 12)")
    environment: str = Field("qa", description="Target environment")

class JiraContext(BaseModel):
    summary: str
    description: str
    acceptance_criteria: List[str]
    steps: List[str]
    issue_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    labels: Optional[List[str]] = None
    components: Optional[List[str]] = None
    reporter: Optional[str] = None
    assignee: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    url: Optional[str] = None  # Add URL field to JiraContext

class WorkflowState(BaseModel):
    request: Annotated[AutomationRequest, LastValue(AutomationRequest)]
    jira_data: Optional[JiraContext] = None
    structured_jira_data: Optional[Dict[str, Any]] = None
    test_plan: Optional[TestPlan] = None
    test_plan_path: Optional[str] = None
    generated_script_path: Optional[str] = None
    execution_results: Optional[ExecutionResult] = None
    generator_name: Optional[str] = None
    executor_name: Optional[str] = None
    retry_count: int = 0
    correction_suggestions: Optional[str] = None
    logs: List[str] = []
