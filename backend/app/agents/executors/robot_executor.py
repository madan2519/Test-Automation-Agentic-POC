import asyncio
from mcp_tools.execution_tool import execution_tool
from schemas.request_schema import WorkflowState
from schemas.response_schema import ExecutionResult, TestCaseResult
from utils.logger import logger

class RobotExecutor:
    async def run(self, state: WorkflowState) -> WorkflowState:
        if state.executor_name != "robot_executor":
            return state
            
        logger.info("RobotExecutor: Starting Robot Framework test execution")
        state.logs.append("RobotExecutor: Starting Robot Framework test execution...")
        
        try:
            # Check if script file exists
            if not state.generated_script_path:
                error_msg = "RobotExecutor: No script file found to execute"
                logger.error(error_msg)
                state.logs.append(error_msg)
                return state
            
            # Quote paths to handle spaces in directory names (consistent with other executors)
            script_path = f'"{state.generated_script_path}"'
            command = f'robot {script_path}'
            
            logger.info(f"RobotExecutor: Running command: {command}")
            state.logs.append(f"RobotExecutor: Executing command: {command}")
            
            # Use execution_tool for consistency (like other executors)
            result = await asyncio.to_thread(execution_tool.run_command, command)
            state.execution_results = result
            logger.info("RobotExecutor: Test execution completed")
            state.logs.append(f"RobotExecutor: Finished. Result: {result.passed} Passed, {result.failed} Failed")
            return state
            
        except Exception as e:
            logger.error(f"RobotExecutor: Error during execution: {str(e)}")
            state.logs.append(f"RobotExecutor: Execution error: {str(e)}")
            
            # Return error state
            results = ExecutionResult(
                tests_run=1,
                passed=0,
                failed=1,
                execution_time="0s",
                test_cases=[
                    TestCaseResult(
                        name="robot_test",
                        status="error",
                        duration="0s",
                        error_message=str(e)
                    )
                ],
                logs=f"Robot Framework execution error: {str(e)}"
            )
            state.execution_results = results
            return state

robot_executor = RobotExecutor()
