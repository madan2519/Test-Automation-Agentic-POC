import asyncio
from mcp_tools.execution_tool import execution_tool
from schemas.request_schema import WorkflowState
from schemas.response_schema import ExecutionResult, TestCaseResult
from utils.logger import logger

class AppiumExecutor:
    async def run(self, state: WorkflowState) -> WorkflowState:
        if state.executor_name != "appium_executor":
            return state
            
        logger.info("AppiumExecutor: Starting Appium test execution")
        state.logs.append("AppiumExecutor: Starting Appium test execution...")
        
        try:
            # Check if script file exists
            if not state.generated_script_path:
                error_msg = "AppiumExecutor: No script file found to execute"
                logger.error(error_msg)
                state.logs.append(error_msg)
                return state
            
            # Quote paths to handle spaces in directory names (consistent with other executors)
            script_path = f'"{state.generated_script_path}"'
            command = f'py -m pytest {script_path}'  # Remove extra quotes for Windows compatibility
            
            logger.info(f"AppiumExecutor: Running command: {command}")
            state.logs.append(f"AppiumExecutor: Executing command: {command}")
            
            # Use execution_tool for consistency (like PlaywrightExecutor and SeleniumExecutor)
            result = await asyncio.to_thread(execution_tool.run_command, command)
            state.execution_results = result
            logger.info("AppiumExecutor: Test execution completed")
            state.logs.append(f"AppiumExecutor: Finished. Result: {result.passed} Passed, {result.failed} Failed")
            return state
            
        except Exception as e:
            logger.error(f"AppiumExecutor: Error during execution: {str(e)}")
            state.logs.append(f"AppiumExecutor: Execution error: {str(e)}")
            
            # Return error state
            results = ExecutionResult(
                tests_run=1,
                passed=0,
                failed=1,
                execution_time="0s",
                test_cases=[
                    TestCaseResult(
                        name="appium_test",
                        status="error",
                        duration="0s",
                        error_message=str(e)
                    )
                ],
                logs=f"Appium execution error: {str(e)}"
            )
            state.execution_results = results
            return state

appium_executor = AppiumExecutor()
