from services.groq_service import groq_service, openai_service
from schemas.request_schema import WorkflowState
from utils.logger import logger
from openai import AsyncOpenAI
from config.settings import settings
from config.llm_config import RETRY_AGENT_MODEL, RETRY_AGENT_TEMPERATURE
import json

class RetryAgent:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def run(self, state: WorkflowState) -> WorkflowState:
        if state.execution_results and state.execution_results.failed > 0:
            if state.retry_count < 1:
                state.retry_count += 1
                
                # Use LLM to analyze failures and generate intelligent corrections
                failure_analysis = await self._llm_analyze_failures(state)
                correction_suggestions = await self._llm_generate_corrections(failure_analysis, state)
                
                logger.info(f"RetryAgent: Test failed. Retrying instance {state.retry_count}/3")
                state.logs.append(f"RetryAgent: LLM Analysis - {failure_analysis}")
                state.logs.append(f"RetryAgent: AI-Generated corrections - {correction_suggestions}")
                state.logs.append(f"RetryAgent: Retrying... (Attempt {state.retry_count}/3)")
                
                # Add correction suggestions to state for script generator to use
                state.correction_suggestions = correction_suggestions
            else:
                logger.warning("RetryAgent: Max retries reached.")
                state.logs.append("RetryAgent: Max retries reached. Moving to commit.")
                state.logs.append("RetryAgent: Final failure analysis - Manual script review required")
        else:
            logger.info("RetryAgent: No failures detected or no results yet.")
            
        return state

    async def _llm_analyze_failures(self, state: WorkflowState) -> str:
        """Use LLM to analyze execution failures intelligently"""
        if not self.openai_client:
            return "LLM analysis not available - using fallback pattern matching"
        
        # Prepare comprehensive failure context for LLM
        failure_context = {
            "execution_results": {
                "total_tests": state.execution_results.tests_run if state.execution_results else 0,
                "passed": state.execution_results.passed if state.execution_results else 0,
                "failed": state.execution_results.failed if state.execution_results else 0,
                "error_output": state.execution_results.logs or "",
                "failed_test_names": [tc.name for tc in state.execution_results.test_cases if tc.status == "failed"] if state.execution_results else [],
                "execution_time": state.execution_results.execution_time if state.execution_results else 0
            },
            "context": {
                "generator_name": state.generator_name,
                "platform": state.request.platform,
                "browser": state.request.browser,
                "device": state.request.device,
                "framework": state.request.framework,
                "language": state.request.language,
                "jira_id": state.request.jira_id
            },
            "structured_requirements": state.structured_jira_data or {}
        }
        
        analysis_prompt = f"""
        Analyze the following test execution failure and provide intelligent insights:

        EXECUTION CONTEXT:
        {json.dumps(failure_context, indent=2)}

        TASK: 
        1. Identify the root cause of failures
        2. Categorize failure patterns (element issues, timing problems, logic errors, environment issues)
        3. Determine if failures are related to locators, waits, assertions, or framework-specific issues
        4. Assess if the test logic needs improvement vs framework implementation issues
        5. Provide specific, actionable recommendations for each failure type

        FRAMEWORK-SPECIFIC CONSIDERATIONS:
        - For Playwright: Consider page.wait_for_selector(), locator strategies, and proper error handling
        - For Selenium: Consider WebDriverWait, explicit waits, and Actions class usage  
        - For Appium: Consider MobileElement waits, touch gestures, and device capabilities

        Return a concise analysis focusing on the most likely root causes and specific fixes needed.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=RETRY_AGENT_MODEL,  # Use global config
                messages=[
                    {"role": "system", "content": "You are an expert QA automation engineer specializing in test failure analysis and debugging. Provide concise, actionable insights."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=RETRY_AGENT_TEMPERATURE  # Use global config
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return f"LLM analysis error: {str(e)}"

    async def _llm_generate_corrections(self, failure_analysis: str, state: WorkflowState) -> str:
        """Use LLM to generate specific correction strategies"""
        if not self.openai_client:
            return "LLM corrections not available - using fallback suggestions"
        
        correction_prompt = f"""
        Based on this failure analysis:
        {failure_analysis}

        And the current automation context:
        - Framework: {state.request.framework}
        - Language: {state.request.language}  
        - Platform: {state.request.platform}
        - Browser: {state.request.browser}
        - Device: {state.request.device}
        - Generator: {state.generator_name}

        Generate specific, actionable correction strategies:

        REQUIREMENTS:
        1. Provide code-level fixes (not just conceptual advice)
        2. Include specific function/method replacements
        3. Suggest exact locator improvements
        4. Recommend wait strategies and timeouts
        5. Address framework-specific best practices
        6. Consider the structured requirements that should be tested

        FORMAT: 
        Return a numbered list of specific corrections that can be directly applied to fix the script.
        Each correction should include: what to change, why it helps, and how to implement.

        Focus on practical, implementable solutions rather than general advice.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=RETRY_AGENT_MODEL,  # Use global config
                messages=[
                    {"role": "system", "content": "You are an expert QA automation engineer specializing in script debugging and optimization. Generate specific, implementable code corrections."},
                    {"role": "user", "content": correction_prompt}
                ],
                temperature=RETRY_AGENT_TEMPERATURE  # Use global config
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM correction generation failed: {e}")
            return f"LLM correction error: {str(e)}"

retry_agent = RetryAgent()
