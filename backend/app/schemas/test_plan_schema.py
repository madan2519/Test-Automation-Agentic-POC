from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class TestCasePriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TestCaseStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    PASSED = "Passed"
    FAILED = "Failed"
    SKIPPED = "Skipped"

class TestStep(BaseModel):
    step_number: int = Field(..., description="Sequential step number")
    action: str = Field(..., description="Action to be performed")
    expected_result: str = Field(..., description="Expected result of the action")
    test_data: Optional[str] = Field(None, description="Test data required for this step")

class TestCase(BaseModel):
    test_case_id: str = Field(..., description="Unique test case identifier")
    title: str = Field(..., description="Test case title")
    description: str = Field(..., description="Detailed test case description")
    priority: TestCasePriority = Field(TestCasePriority.MEDIUM, description="Test case priority")
    status: TestCaseStatus = Field(TestCaseStatus.PENDING, description="Test case status")
    platform: str = Field(..., description="Target platform (Web, Mobile, API)")
    framework: str = Field(..., description="Test automation framework")
    preconditions: Optional[str] = Field(None, description="Preconditions for the test")
    test_steps: List[TestStep] = Field(..., description="List of test steps")
    expected_outcome: str = Field(..., description="Overall expected outcome")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    estimated_time: Optional[int] = Field(None, description="Estimated execution time in minutes")

class TestPlan(BaseModel):
    test_plan_id: str = Field(..., description="Unique test plan identifier")
    jira_id: str = Field(..., description="Source Jira ticket ID")
    title: str = Field(..., description="Test plan title")
    description: str = Field(..., description="Test plan description")
    platform: str = Field(..., description="Target platform for all test cases")
    framework: str = Field(..., description="Primary framework to be used")
    test_cases: List[TestCase] = Field(..., description="List of test cases")
    total_test_cases: int = Field(..., description="Total number of test cases")
    created_at: str = Field(..., description="Creation timestamp")
    version: str = Field("1.0", description="Test plan version")
    coverage_areas: List[str] = Field(default_factory=list, description="Areas covered by this test plan")
    
    def get_test_cases_by_priority(self, priority: TestCasePriority) -> List[TestCase]:
        """Filter test cases by priority"""
        return [tc for tc in self.test_cases if tc.priority == priority]
    
    def get_test_cases_by_status(self, status: TestCaseStatus) -> List[TestCase]:
        """Filter test cases by status"""
        return [tc for tc in self.test_cases if tc.status == status]
