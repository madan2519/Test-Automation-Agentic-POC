from services.groq_service import groq_service, openai_service
from mcp_tools.script_writer_tool import script_writer_tool
from schemas.request_schema import WorkflowState
from utils.logger import logger

class PythonAppiumAgent:
    async def run(self, state: WorkflowState) -> WorkflowState:
        if state.generator_name != "python_appium_agent":
            return state
            
        logger.info("PythonAppiumAgent generating script")
        state.logs.append("PythonAppiumAgent: Generating Appium mobile script...")
        
        if not state.structured_jira_data:
            error_msg = "PythonAppiumAgent: Missing structured Jira data. Cannot generate script."
            logger.error(error_msg)
            state.logs.append(error_msg)
            return state
        
        platform_info = f"Platform: {state.request.platform}"
        if state.request.device:
            platform_info += f", Device: {state.request.device}"

        # Extract functional requirements from structured data
        functional_requirements = state.structured_jira_data.get('functional_requirements', [])
        req_summary = state.structured_jira_data.get('ticket_summary', 'Unknown')
        
        system_prompt = f"You are an expert QA Automation Engineer specialized in Appium. Generate only valid Python Appium code. {platform_info}"
        prompt = f"""
        Generate an Appium test script in Python for the following structured requirements:
        {platform_info}
        Summary: {req_summary}
        Functional Requirements: {functional_requirements}
        
        Guidelines:
        - Include proper Appium imports (Appium-Python-Client).
        - Use `webdriver.Remote()` with typical `desired_capabilities` for specified {state.request.platform}.
        - For {state.request.device}, include it in capabilities if appropriate.
        - Ensure script is self-contained.
        - Generate test cases based on Given-When-Then acceptance criteria from functional requirements.
        - Include proper waits and error handling.
        - Add assertions to verify test outcomes.
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
        state.logs.append(f"PythonAppiumAgent: Script saved to {path}")
        
        return state

python_appium_agent = PythonAppiumAgent()
