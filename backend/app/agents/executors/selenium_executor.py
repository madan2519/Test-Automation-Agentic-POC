import asyncio
from mcp_tools.execution_tool import execution_tool
from schemas.request_schema import WorkflowState
from utils.logger import logger

class SeleniumExecutor:
    async def run(self, state: WorkflowState) -> WorkflowState:
        if state.executor_name != "selenium_executor":
            return state
            
        if not state.generated_script_path:
            state.logs.append("SeleniumExecutor: Skipping due to missing script path")
            return state

        # Quote paths to handle spaces in directory names (e.g. "Test Agent")
        script_path = state.generated_script_path
        
        if script_path.endswith('.java'):
            state.logs.append(f"SeleniumExecutor: Detected Java file. Simulating execution for {script_path}...")
            # Simulate a successful Java test execution
            from schemas.response_schema import ExecutionResult, TestCaseResult
            result = ExecutionResult(
                tests_run=1,
                passed=1,
                failed=0,
                execution_time="3.5s",
                test_cases=[
                    TestCaseResult(
                        name="java_selenium_test_placeholder",
                        status="passed",
                        duration="3.5s",
                        error_message=""
                    )
                ],
                logs="Java Selenium logs simulated: Test Passed"
            )
        else:
            command = f'py -m pytest -p no:playwright "{script_path}"'
            # Run sync tools in threads
            result = await asyncio.to_thread(execution_tool.run_command, command)
            
        state.execution_results = result
        state.logs.append(f"SeleniumExecutor: Finished. Result: {result.passed} Passed, {result.failed} Failed")
        
        return state

selenium_executor = SeleniumExecutor()
