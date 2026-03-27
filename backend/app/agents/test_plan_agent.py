import json
import os
from datetime import datetime
from typing import Dict, Any, List
from groq import Groq
from services.groq_service import groq_service, openai_service
from schemas.request_schema import WorkflowState, JiraContext
from schemas.test_plan_schema import TestPlan, TestCase, TestCasePriority
from utils.logger import logger
from config.llm_config import TEST_PLAN_MODEL, TEST_PLAN_TEMPERATURE
from openai import AsyncOpenAI
from config.settings import settings
import uuid

class TestPlanAgent:
    def __init__(self):
        self.groq_client = groq_service
        self.openai_client = openai_service
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        # Use the test_case_folder from settings, create it if it doesn't exist
        self.test_case_files_dir = os.path.join(settings.SCRIPT_STORAGE_PATH, "test_case_files")
        os.makedirs(self.test_case_files_dir, exist_ok=True)
        logger.info(f"TestPlanAgent initialized. Test plans will be saved to: {self.test_case_files_dir}")

    async def run(self, state: WorkflowState) -> WorkflowState:
        """Combined agent: Structure Jira ticket AND generate test plan"""
        try:
            logger.info("Starting combined Jira structuring and test plan generation")
            
            jira_data = state.jira_data
            if not jira_data:
                raise ValueError("Jira data not found in state")
            
            # Step 1: Structure the Jira ticket using AI (from StructuringAgent)
            structured_data = await self._structure_jira_ticket(jira_data)
            state.structured_jira_data = structured_data
            state.logs.append("Successfully structured Jira ticket into acceptance criteria")
            
            # Step 2: Generate test plan from structured data (from TestPlanAgent)
            test_plan = await self._generate_test_plan(structured_data, state.request)
            state.test_plan = test_plan
            
            # Save test plan to file
            test_plan_path = await self._save_test_plan(test_plan, state.request.jira_id, state.request.platform, state.request.framework)
            state.test_plan_path = test_plan_path
            
            state.logs.append(f"Test plan generated and saved: {test_plan_path}")
            logger.info("Combined Jira structuring and test plan generation completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Error in test plan generation: {str(e)}")
            state.logs.append(f"Test plan generation failed: {str(e)}")
            raise

    async def _generate_test_plan_from_structured_data(self, structured_data: Dict[str, Any], request) -> TestPlan:
        """Generate test plan using AI model from structured data"""
        
        # Create prompt for AI
        prompt = self._create_test_plan_prompt_from_structured_data(structured_data, request)
        
        try:
            # Try OpenAI first, fallback to Groq
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert QA engineer specializing in test case design and automation. Generate comprehensive test plans."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                ai_response = response.choices[0].message.content
            else:
                # Fallback to Groq
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert QA engineer specializing in test case design and automation. Generate comprehensive test plans."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                ai_response = response.choices[0].message.content
            
            # Parse the AI response
            test_plan = self._parse_ai_response_to_test_plan(ai_response, structured_data, request)
            return test_plan
            
        except Exception as e:
            logger.error(f"Error in AI test plan generation: {str(e)}")
            raise

    async def _generate_test_plan(self, jira_data: JiraContext, request) -> TestPlan:
        """Generate test plan using AI model"""
        
        # Create prompt for AI
        prompt = self._create_test_plan_prompt(jira_data, request)
        
        try:
            # Try OpenAI first (uncommented), fallback to Groq
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model=TEST_PLAN_MODEL,  # Use global config
                    messages=[
                        {"role": "system", "content": f"You are an expert QA Automation Engineer. Create comprehensive test plans. {request.platform}"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=TEST_PLAN_TEMPERATURE  # Use global config
                )
                ai_response = response.choices[0].message.content
            else:
                # Use Groq
                response = self.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert QA engineer creating comprehensive test plans."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                ai_response = response.choices[0].message.content
            
            # Parse AI response into structured test plan
            test_plan = self._parse_ai_response_to_test_plan(ai_response, jira_data, request)
            
            return test_plan
            
        except Exception as e:
            logger.error(f"AI model error: {str(e)}")
            # Fallback to basic test plan generation
            return self._create_basic_test_plan(jira_data, request)

    def _create_test_plan_prompt_from_structured_data(self, structured_data: Dict[str, Any], request) -> str:
        """Create prompt for test plan generation from structured Jira data"""
        
        # Extract functional requirements and format them for test generation
        functional_requirements = structured_data.get('functional_requirements', [])
        
        # Build a formatted string of requirements for the prompt
        req_summary = []
        for req in functional_requirements:
            req_summary.append(f"ID: {req.get('id', 'N/A')}")
            req_summary.append(f"Title: {req.get('title', 'N/A')}")
            req_summary.append(f"Priority: {req.get('priority', 'N/A')}")
            req_summary.append(f"User Flow: {req.get('user_flow', 'N/A')}")
            req_summary.append(f"Source: {req.get('source', 'N/A')}")
            req_summary.append("Acceptance Criteria:")
            
            for ac in req.get('acceptance_criteria', []):
                req_summary.append(f"  AC{ac.get('id', 'N/A')}:")
                req_summary.append(f"    Given: {ac.get('given', 'N/A')}")
                req_summary.append(f"    When: {ac.get('when', 'N/A')}")
                req_summary.append(f"    Then: {ac.get('then', 'N/A')}")
            
            req_summary.append("---")
        
        prompt = f"""Generate comprehensive test cases for the following structured requirements:

TICKET SUMMARY:
{structured_data.get('ticket_summary', 'No summary available')}

FUNCTIONAL REQUIREMENTS:
{chr(10).join(req_summary)}

TEST REQUIREMENTS:
- Platform: {request.platform}
- Language: {request.language}
- Framework: {request.framework}
- Browser: {request.browser or 'Not specified'}
- Device: {request.device or 'Not specified'}
- Environment: {request.environment}

INSTRUCTIONS:
1. Create test cases for ALL functional requirements and their acceptance criteria
2. Each acceptance criterion should have at least one corresponding test case
3. Convert Given-When-Then format into actionable test steps
4. Consider the priority levels specified in the requirements
5. Include positive, negative, and edge case scenarios based on the acceptance criteria
6. Group test cases by user flow where applicable
7. Ensure test steps are specific and actionable
8. Provide realistic time estimates

RESPONSE FORMAT (JSON):
{{
    "test_cases": [
        {{
            "title": "Test case title",
            "description": "Detailed description linking to requirement and acceptance criteria",
            "priority": "Critical|High|Medium|Low",
            "preconditions": "Any preconditions",
            "test_steps": [
                {{
                    "step_number": 1,
                    "action": "Action to perform",
                    "expected_result": "Expected outcome",
                    "test_data": "Test data if needed"
                }}
            ],
            "expected_outcome": "Overall expected result",
            "tags": ["tag1", "tag2"],
            "estimated_time": 15
        }}
    ],
    "coverage_areas": ["functional", "user-flows"],
    "requirement_coverage": {{
        "total_requirements": {len(functional_requirements)},
        "total_acceptance_criteria": {sum(len(req.get('acceptance_criteria', [])) for req in functional_requirements)},
        "test_cases_generated": "number_of_test_cases"
    }}
}}

Generate a complete, structured test plan in valid JSON format."""
        return prompt

    def _create_test_plan_prompt(self, jira_data: JiraContext, request) -> str:
        """Create detailed prompt for AI test plan generation"""
        
        prompt = f"""
Based on the following Jira ticket details, create a comprehensive test plan:

JIRA TICKET DETAILS:
- ID: {jira_data.summary}
- Summary: {jira_data.summary}
- Description: {jira_data.description}
- Acceptance Criteria: {jira_data.acceptance_criteria}
- Steps: {jira_data.steps}

TEST REQUIREMENTS:
- Platform: {request.platform}
- Language: {request.language}
- Framework: {request.framework}
- Browser: {request.browser or 'Not specified'}
- Device: {request.device or 'Not specified'}
- Environment: {request.environment}

INSTRUCTIONS:
1. Create multiple test cases covering all acceptance criteria
2. Each test case should have clear, actionable steps
3. Consider the specified platform and framework
4. Include positive, negative, and edge case scenarios
5. Assign appropriate priority levels
6. Provide realistic time estimates

RESPONSE FORMAT (JSON):
{{
    "test_cases": [
        {{
            "title": "Test case title",
            "description": "Detailed description",
            "priority": "Critical|High|Medium|Low",
            "preconditions": "Any preconditions",
            "test_steps": [
                {{
                    "step_number": 1,
                    "action": "Action to perform",
                    "expected_result": "Expected outcome",
                    "test_data": "Test data if needed"
                }}
            ],
            "expected_outcome": "Overall expected result",
            "tags": ["tag1", "tag2"],
            "estimated_time": 15
        }}
    ],
    "coverage_areas": ["area1", "area2"]
}}

Generate a complete, structured test plan in valid JSON format.
"""
        return prompt

    def _parse_ai_response_to_test_plan(self, ai_response: str, structured_data: Dict[str, Any], request) -> TestPlan:
        """Parse AI response into TestPlan object"""
        try:
            # Extract JSON from response
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in AI response")
            
            json_str = ai_response[json_start:json_end]
            data = json.loads(json_str)
            
            # Get ticket summary from structured data
            ticket_summary = structured_data.get('ticket_summary', 'Unknown')
            ticket_id = ticket_summary.split()[0] if ticket_summary else 'UNKNOWN'
            
            # Create test cases
            test_cases = []
            for i, tc_data in enumerate(data.get('test_cases', [])):
                test_steps = []
                for step_data in tc_data.get('test_steps', []):
                    test_step = TestStep(
                        step_number=step_data.get('step_number', len(test_steps) + 1),
                        action=step_data.get('action', ''),
                        expected_result=step_data.get('expected_result', ''),
                        test_data=step_data.get('test_data')
                    )
                    test_steps.append(test_step)
                
                test_case = TestCase(
                    test_case_id=f"TC_{ticket_id}_{i+1:03d}",
                    title=tc_data.get('title', ''),
                    description=tc_data.get('description', ''),
                    priority=TestCasePriority(tc_data.get('priority', 'Medium')),
                    platform=request.platform,
                    framework=request.framework,
                    preconditions=tc_data.get('preconditions'),
                    test_steps=test_steps,
                    expected_outcome=tc_data.get('expected_outcome', ''),
                    tags=tc_data.get('tags', []),
                    estimated_time=tc_data.get('estimated_time')
                )
                test_cases.append(test_case)
            
            # Create test plan
            test_plan = TestPlan(
                test_plan_id=f"TP_{ticket_id}_{uuid.uuid4().hex[:8]}",
                jira_id=ticket_summary,
                title=f"Test Plan for {ticket_summary}",
                description=f"Automated test plan generated from structured requirements: {ticket_summary}",
                platform=request.platform,
                framework=request.framework,
                test_cases=test_cases,
                total_test_cases=len(test_cases),
                created_at=datetime.now().isoformat(),
                coverage_areas=data.get('coverage_areas', [])
            )
            
            return test_plan
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            # Fallback to basic test plan
            return self._create_basic_test_plan(structured_data, request)

    def _create_basic_test_plan(self, structured_data: Dict[str, Any], request) -> TestPlan:
        """Create a basic test plan when AI parsing fails"""
        
        # Get ticket summary from structured data
        ticket_summary = structured_data.get('ticket_summary', 'Unknown')
        ticket_id = ticket_summary.split()[0] if ticket_summary else 'UNKNOWN'
        
        # Create a basic test case from functional requirements
        test_steps = []
        functional_requirements = structured_data.get('functional_requirements', [])
        
        for req in functional_requirements:
            for ac in req.get('acceptance_criteria', []):
                # Create a test step from Given-When-Then
                given = ac.get('given', '')
                when = ac.get('when', '')
                then = ac.get('then', '')
                
                action = f"Given: {given}\nWhen: {when}"
                expected_result = then
                
                test_step = TestStep(
                    step_number=len(test_steps) + 1,
                    action=action,
                    expected_result=expected_result,
                    test_data=None
                )
                test_steps.append(test_step)
        
        # Create test case
        test_case = TestCase(
            test_case_id=f"TC_{ticket_id}_001",
            title=f"Basic Test Case for {ticket_summary}",
            description="Basic test case generated from structured requirements",
            priority=TestCasePriority.MEDIUM,
            platform=request.platform,
            framework=request.framework,
            preconditions=None,
            test_steps=test_steps,
            expected_outcome="All acceptance criteria are verified",
            tags=["basic", "fallback"],
            estimated_time=30
        )
        
        # Create test plan
        test_plan = TestPlan(
            test_plan_id=f"TP_{ticket_id}_{uuid.uuid4().hex[:8]}",
            jira_id=ticket_summary,
            title=f"Basic Test Plan for {ticket_summary}",
            description="Basic test plan generated from structured requirements",
            platform=request.platform,
            framework=request.framework,
            test_cases=[test_case],
            total_test_cases=1,
            created_at=datetime.now().isoformat(),
            coverage_areas=["basic"]
        )
        
        return test_plan

    async def _save_test_plan(self, test_plan: TestPlan, request) -> str:
        """Save test plan to file with proper naming convention"""
        try:
            # Extract platform and framework from request
            platform = request.platform.lower().replace(" ", "_")
            framework = request.framework.lower().replace(" ", "_")
            jira_id = request.jira_id.replace("POC-", "POC-").replace("/", "_")
            
            # Ensure directory exists automatically
            os.makedirs(self.test_case_files_dir, exist_ok=True)
            
            # Create filename with script naming convention: test_jiraticketid_platform_framework.txt
            filename = f"test_{jira_id}_{platform}_{framework}.txt"
            filepath = os.path.join(self.test_case_files_dir, filename)
            
            # Generate human-readable test plan content with proper Jira ID
            test_plan_content = self._generate_test_plan_content(test_plan, request, jira_id)
            
            # Save as text file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(test_plan_content)
            
            logger.info(f"Test plan automatically saved to: {filepath}")
            logger.info(f"Test plan contains {len(test_plan.test_cases)} test cases")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save test plan: {str(e)}")
            raise

    def _generate_test_plan_content(self, test_plan: TestPlan, request, jira_id: str) -> str:
        """Generate human-readable test plan content for text file"""
        content = f"""
========================================
TEST PLAN: {test_plan.title.upper()}
========================================

Test Plan ID: {test_plan.test_plan_id}
Jira ID: {jira_id}
Platform: {test_plan.platform}
Framework: {test_plan.framework}
Created: {test_plan.created_at}
Total Test Cases: {test_plan.total_test_cases}

DESCRIPTION:
{test_plan.description}

COVERAGE AREAS:
{', '.join(test_plan.coverage_areas)}

----------------------------------------
TEST CASES
----------------------------------------

"""
        
        for i, test_case in enumerate(test_plan.test_cases, 1):
            content += f"""
TEST CASE {i}: {test_case.title.upper()}
========================================
Test Case ID: {test_case.test_case_id}
Priority: {test_case.priority}
Platform: {test_case.platform}
Framework: {test_case.framework}
Estimated Time: {test_case.estimated_time} minutes
Tags: {', '.join(test_case.tags) if test_case.tags else 'None'}

Description:
{test_case.description}

Preconditions:
{test_case.preconditions if test_case.preconditions else 'None'}

Expected Outcome:
{test_case.expected_outcome}

TEST STEPS:
"""
            
            for step in test_case.test_steps:
                content += f"""
Step {step.step_number}:
  Action: {step.action}
  Expected Result: {step.expected_result}
  Test Data: {step.test_data if step.test_data else 'None'}
"""
            
            content += "\n" + "="*60 + "\n"
        
        content += f"""
========================================
END OF TEST PLAN
========================================
Generated by AI Automation Platform
Framework: {request.framework}
Platform: {request.platform}
Language: {request.language}
"""
        
        return content

    def _test_plan_to_markdown(self, test_plan: TestPlan) -> str:
        """Convert test plan to markdown format"""
        md = f"""# Test Plan: {test_plan.title}

**Test Plan ID:** {test_plan.test_plan_id}  
**Jira ID:** {test_plan.jira_id}  
**Platform:** {test_plan.platform}  
**Framework:** {test_plan.framework}  
**Created:** {test_plan.created_at}  
**Total Test Cases:** {test_plan.total_test_cases}

## Description
{test_plan.description}

## Coverage Areas
{', '.join(test_plan.coverage_areas)}

---

## Test Cases

"""
        
        for tc in test_plan.test_cases:
            md += f"""### {tc.test_case_id}: {tc.title}

**Priority:** {tc.priority}  
**Status:** {tc.status}  
**Estimated Time:** {tc.estimated_time if tc.estimated_time else 'N/A'} minutes 
**Tags:** {', '.join(tc.tags) if tc.tags else 'None'}

**Description:** {tc.description}

**Preconditions:** {tc.preconditions if tc.preconditions else 'None'}

**Expected Outcome:** {tc.expected_outcome}

**Test Steps:**
"""
            
            for step in tc.test_steps:
                md += f"""
{step.step_number}. **Action:** {step.action}  
   **Expected Result:** {step.expected_result}
   **Test Data:** {step.test_data if step.test_data else 'None'}
"""
            
            md += "\n---\n\n"
        
        return md

# Create agent instance
test_plan_agent = TestPlanAgent()
