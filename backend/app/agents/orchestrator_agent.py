from schemas.request_schema import WorkflowState
from schemas.test_plan_schema import TestCasePriority
from utils.logger import logger
from openai import AsyncOpenAI
from config.settings import settings
from config.llm_config import ORCHESTRATOR_MODEL, ORCHESTRATOR_TEMPERATURE
import json

class OrchestratorAgent:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def run(self, state: WorkflowState) -> WorkflowState:
        logger.info("OrchestratorAgent selecting generator and executor using LLM intelligence")
        
        # Analyze test plan if available
        test_plan_info = self._analyze_test_plan(state)
        
        # Use LLM to determine optimal generator and executor
        generator_name, executor_name = await self._llm_select_agents(state)
        
        if not state.jira_data:
            state.logs.append("Orchestrator: Skipping due to missing Jira data")
            return state

        if not state.structured_jira_data:
            state.logs.append("Orchestrator: Skipping due to missing structured Jira data")
            return state

        state.generator_name = generator_name
        state.executor_name = executor_name
        
        # Add test plan insights to logs
        if state.test_plan:
            state.logs.append(f"Orchestrator: Test plan analysis - {test_plan_info}")
        
        state.logs.append(f"Orchestrator: LLM selected {generator_name} and {executor_name}")
        return state
    
    async def _llm_select_agents(self, state: WorkflowState) -> tuple[str, str]:
        """Use LLM to intelligently select generator and executor based on context"""
        if not self.openai_client:
            logger.warning("LLM not available, using fallback logic")
            return self._fallback_routing(state)
        
        # Prepare context for LLM
        context = {
            "request": {
                "jira_id": state.request.jira_id,
                "platform": state.request.platform,
                "language": state.request.language,
                "framework": state.request.framework,
                "browser": state.request.browser,
                "device": state.request.device,
                "environment": state.request.environment
            },
            "test_plan": {
                "has_test_plan": bool(state.test_plan),
                "total_test_cases": len(state.test_plan.test_cases) if state.test_plan else 0,
                "coverage_areas": state.test_plan.coverage_areas if state.test_plan else []
            },
            "structured_requirements": state.structured_jira_data or {}
        }
        
        # Extract user preferences from state
        user_platform = state.request.platform
        user_language = state.request.language
        user_framework = state.request.framework
        user_browser = state.request.browser
        user_device = state.request.device
        jira_summary = state.jira_data.summary if state.jira_data else "Unknown"
        
        prompt = f"""
        User has requested automation with these specific preferences:
        
        PLATFORM: {user_platform}
        LANGUAGE: {user_language}
        FRAMEWORK: {user_framework}
        BROWSER: {user_browser or 'Not specified'}
        DEVICE: {user_device or 'Not specified'}
        
        JIRA TICKET: {jira_summary}
        
        Based on the user's explicit framework selection: "{user_framework}"
        
        Select the EXACT generator and executor that matches the user's choice:
        
        AVAILABLE OPTIONS:
        - If user selected "Selenium" → python_selenium_agent + selenium_executor
        - If user selected "Playwright" → python_playwright_agent + playwright_executor
        - If user selected "Appium" → python_appium_agent + appium_executor
        - If user selected "Robot Framework" → python_playwright_agent + robot_executor
        
        RULES:
        1. ALWAYS match the user's framework selection exactly
        2. For Web + Appium: Use python_appium_agent + appium_executor
        3. For Web + Robot Framework: Use python_playwright_agent + robot_executor
        4. For Mobile (Android/iOS): Always use python_appium_agent + appium_executor
        
        Respond in this exact format:
        GENERATOR: <generator_name>
        EXECUTOR: <executor_name>
        
        Example responses:
        - If user selected Appium: GENERATOR: python_appium_agent, EXECUTOR: appium_executor
        - If user selected Playwright: GENERATOR: python_playwright_agent, EXECUTOR: playwright_executor
        - If user selected Robot Framework: GENERATOR: python_playwright_agent, EXECUTOR: robot_executor
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=ORCHESTRATOR_MODEL,  # Use global config
                messages=[
                    {"role": "system", "content": "You are an expert automation architect. Select optimal generator and executor based on requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=ORCHESTRATOR_TEMPERATURE  # Use global config
            )
            
            llm_response = response.choices[0].message.content.strip()
            
            # Parse LLM response
            generator_name = ""
            executor_name = ""
            
            for line in llm_response.split('\n'):
                if line.startswith('GENERATOR:'):
                    generator_name = line.split('GENERATOR:')[1].strip()
                elif line.startswith('EXECUTOR:'):
                    executor_name = line.split('EXECUTOR:')[1].strip()
            
            if generator_name and executor_name:
                logger.info(f"LLM selected: {generator_name} + {executor_name}")
                return generator_name, executor_name
            else:
                logger.warning(f"LLM response parsing failed: {llm_response}")
                return self._fallback_routing(state)
                
        except Exception as e:
            logger.error(f"LLM selection failed: {e}")
            return self._fallback_routing(state)
    
    def _fallback_routing(self, state: WorkflowState) -> tuple[str, str]:
        """Fallback routing logic when LLM is unavailable"""
        platform = state.request.platform.lower()
        language = state.request.language.lower()
        framework = state.request.framework.lower()
        
        # Deterministic fallback logic
        if platform == "web":
            if language == "python":
                if framework == "selenium":
                    return "python_selenium_agent", "selenium_executor"
                elif framework == "playwright":
                    return "python_playwright_agent", "playwright_executor"
                elif framework == "appium":
                    return "python_appium_agent", "appium_executor"
                elif framework == "robot framework":
                    return "python_playwright_agent", "robot_executor"
                else:
                    return "python_playwright_agent", "playwright_executor"
            elif language == "java" and framework == "selenium":
                return "java_selenium_agent", "selenium_executor"
        elif platform in ["android", "ios"]:
            return "python_appium_agent", "appium_executor"
        
        logger.warning(f"No specific agent found for {platform}/{language}/{framework}. Using fallback.")
        return "python_playwright_agent", "playwright_executor"
    
    def _analyze_test_plan(self, state: WorkflowState) -> str:
        """Analyze test plan to provide insights for routing decisions"""
        if not state.test_plan:
            return "No test plan available"
        
        test_plan = state.test_plan
        critical_cases = len(test_plan.get_test_cases_by_priority(TestCasePriority.CRITICAL))
        high_cases = len(test_plan.get_test_cases_by_priority(TestCasePriority.HIGH))
        total_cases = test_plan.total_test_cases
        
        analysis = f"{total_cases} test cases"
        if critical_cases > 0:
            analysis += f", {critical_cases} critical"
        if high_cases > 0:
            analysis += f", {high_cases} high priority"
        
        # Add complexity assessment
        avg_steps = sum(len(tc.test_steps) for tc in test_plan.test_cases) / total_cases if total_cases > 0 else 0
        if avg_steps > 5:
            analysis += ", high complexity"
        elif avg_steps > 3:
            analysis += ", medium complexity"
        else:
            analysis += ", low complexity"
        
        return analysis

orchestrator_agent = OrchestratorAgent()
