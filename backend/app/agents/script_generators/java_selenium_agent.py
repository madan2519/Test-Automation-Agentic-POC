from services.groq_service import groq_service, openai_service
from mcp_tools.script_writer_tool import script_writer_tool
from schemas.request_schema import WorkflowState
from utils.logger import logger

class JavaSeleniumAgent:
    async def run(self, state: WorkflowState) -> WorkflowState:
        if state.generator_name != "java_selenium_agent":
            return state
            
        logger.info("JavaSeleniumAgent generating script")
        state.logs.append("JavaSeleniumAgent: Generating Java Selenium script...")
        
        if not state.structured_jira_data:
            error_msg = "JavaSeleniumAgent: Missing structured Jira data. Cannot generate script."
            logger.error(error_msg)
            state.logs.append(error_msg)
            return state
        
        platform_info = f"Platform: {state.request.platform}"
        if state.request.browser:
            platform_info += f", Browser: {state.request.browser}"
        if state.request.device:
            platform_info += f", Device: {state.request.device}"

        # Extract functional requirements from structured data
        functional_requirements = state.structured_jira_data.get('functional_requirements', [])
        req_summary = state.structured_jira_data.get('ticket_summary', 'Unknown')

        system_prompt = f"You are an expert QA Automation Engineer specialized in Java Selenium. Generate only valid Java Selenium code (JUnit or TestNG). {platform_info}"
        prompt = f"""
        Generate a Selenium test script in Java for the following structured requirements:
        {platform_info}
        Summary: {req_summary}
        Functional Requirements: {functional_requirements}
        
        Guidelines:
        - Use Selenium WebDriver and JUnit 5.
        - Include proper imports.
        - Ensure class name is descriptive.
        - Ensure code is self-contained (assume relevant dependencies are on classpath).
        - Generate test methods based on Given-When-Then acceptance criteria from functional requirements.
        - Include proper waits and error handling.
        - Add assertions to verify test outcomes.
        - **IMPORTANT**: If an element is intercepted or not clickable (common on demoqa.com due to ads), use `JavascriptExecutor.executeScript("arguments[0].click();", element)` or scroll to element into view first.
        """
        
        # script_content = await groq_service.generate_response(prompt, system_prompt)
        script_content = await openai_service.generate_response(prompt, system_prompt)
        
        # Clean up code blocks if present
        if "```java" in script_content:
            script_content = script_content.split("```java")[1].split("```")[0].strip()
        elif "```" in script_content:
             script_content = script_content.split("```")[1].split("```")[0].strip()
        
        import asyncio
        # Unique filename based on all parameters
        browser_or_device = state.request.browser or state.request.device or "none"
        param_suffix = f"{state.request.platform.lower()}_{browser_or_device.lower().replace(' ', '_')}_{state.request.language.lower()}_{state.request.framework.lower().replace(' ', '_')}"
        filename = f"test_{state.request.jira_id}_{param_suffix}.java"
        path = await asyncio.to_thread(script_writer_tool.write_script, filename, script_content)
        
        state.generated_script_path = path
        state.logs.append(f"JavaSeleniumAgent: Script saved to {path}")
        
        return state

java_selenium_agent = JavaSeleniumAgent()
