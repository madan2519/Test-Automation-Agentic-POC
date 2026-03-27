import asyncio
from mcp_tools.execution_tool import execution_tool
from schemas.request_schema import WorkflowState
from utils.logger import logger

class PlaywrightExecutor:
    async def run(self, state: WorkflowState) -> WorkflowState:
        if state.executor_name != "playwright_executor":
            return state
            
        logger.info("PlaywrightExecutor: Starting execution...")
        state.logs.append("PlaywrightExecutor: Starting execution...")

        if not state.generated_script_path:
            logger.warning("PlaywrightExecutor: Missing script path")
            state.logs.append("PlaywrightExecutor: Skipping due to missing script path")
            return state

        # Quote paths to handle spaces in directory names (e.g. "Test Agent")
        script_path = f'"{state.generated_script_path}"'
        command = f'py -m pytest {script_path}'
        
        logger.info(f"PlaywrightExecutor: Running command: {command}")
        
        # Run sync tools in threads
        try:
            result = await asyncio.to_thread(execution_tool.run_command, command)
            state.execution_results = result
            logger.info("PlaywrightExecutor: Command completed successfully")
            state.logs.append(f"PlaywrightExecutor: Finished. Result: {result.passed} Passed, {result.failed} Failed")
        except Exception as e:
            logger.error(f"PlaywrightExecutor: Fatal error during command: {e}")
            state.logs.append(f"PlaywrightExecutor Error: {str(e)}")
        
        logger.info("PlaywrightExecutor: Exiting")
        return state

playwright_executor = PlaywrightExecutor()
