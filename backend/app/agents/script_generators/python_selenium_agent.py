from services.groq_service import groq_service, openai_service
from mcp_tools.script_writer_tool import script_writer_tool
from schemas.request_schema import WorkflowState
from utils.logger import logger

class PythonSeleniumAgent:
    async def run(self, state: WorkflowState) -> WorkflowState:
        if state.generator_name != "python_selenium_agent":
            return state
            
        logger.info("PythonSeleniumAgent generating script")
        state.logs.append("PythonSeleniumAgent: Generating Selenium script...")
        
        if not state.structured_jira_data:
            error_msg = "PythonSeleniumAgent: Missing structured Jira data. Cannot generate script."
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
        application_url = state.structured_jira_data.get('application_url') or \
                       (state.jira_data.url if state.jira_data and hasattr(state.jira_data, 'url') else None)

        system_prompt = f"You are an expert QA Automation Engineer. Generate only valid Python Selenium code. {platform_info}"
        prompt = f"""
        Generate a Selenium test script in Python using pytest for the following structured requirements:
        {platform_info}
        Summary: {req_summary}
        Application URL: {application_url or 'Not specified'}
        Functional Requirements: {functional_requirements}
        
        Guidelines:
        - Use `webdriver.{state.request.browser or "Chrome"}()` with headless options.
        - If "Edge" is requested, use `webdriver.Edge()`.
        - Include proper imports and setup.
        - Ensure the code is self-contained (assume relevant dependencies are on the classpath).
        - Use pytest style if possible.
        - Generate test methods based on Given-When-Then acceptance criteria from functional requirements.
        - Include proper waits and error handling.
        - Add assertions to verify test outcomes.
        - **IMPORTANT**: Use the application URL: {application_url or 'https://thinking-tester-contact-list.herokuapp.com/'} for navigation
        - **IMPORTANT**: Do NOT use example.com or dummy URLs - use the actual application URL provided.
        - **IMPORTANT**: If an element is intercepted or not clickable (common on demoqa.com due to ads), use `driver.execute_script("arguments[0].click();", element)` or scroll the element into view first.
        """
        
        # script_content = await groq_service.generate_response(prompt, system_prompt)
        script_content = await openai_service.generate_response(prompt, system_prompt)
        
        # Clean up code blocks if present
        if "```python" in script_content:
            script_content = script_content.split("```python")[1].split("```")[0].strip()
        
        import asyncio
        # Unique filename based on all parameters
        browser_or_device = state.request.browser or state.request.device or "none"
        param_suffix = f"{state.request.platform.lower()}_{browser_or_device.lower().replace(' ', '_')}_{state.request.language.lower()}_{state.request.framework.lower().replace(' ', '_')}"
        filename = f"test_{state.request.jira_id}_{param_suffix}.py"
        path = await asyncio.to_thread(script_writer_tool.write_script, filename, script_content)
        
        state.generated_script_path = path
        state.logs.append(f"PythonSeleniumAgent: Script saved to {path}")
        
        return state

python_selenium_agent = PythonSeleniumAgent()
