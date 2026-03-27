import asyncio
from mcp_tools.jira_comment_tool import jira_comment_tool
from schemas.request_schema import WorkflowState
from utils.logger import logger

class CommitAgent:
    def _build_results_table(self, state: WorkflowState) -> str:
        """Build a rich Jira-formatted results table."""
        results = state.execution_results
        
        if not results:
            return "*Automation Execution Results*\n- *Status:* (x) FAILED (Workflow aborted before execution)"

        overall_status = "(/) *PASSED*" if results.failed == 0 else "(x) *FAILED*"
        
        # Build header section
        header = (
            f"h2. Automation Execution Results\n\n"
            f"|| Metric || Value ||\n"
            f"| *Overall Status* | {overall_status} |\n"
            f"| *Tests Run* | {results.tests_run} |\n"
            f"| *Passed* | (/) {results.passed} |\n"
            f"| *Failed* | (x) {results.failed} |\n"
            f"| *Total Duration* | {results.execution_time} |\n\n"
        )
        
        # Build test cases table
        cases_table = (
            "h3. Test Case Results\n\n"
            "|| # || Test Case || Status || Duration || Error ||\n"
        )
        
        for i, tc in enumerate(results.test_cases, 1):
            status_icon = "(/) Passed" if tc.status == "passed" else "(x) Failed" if tc.status == "failed" else "(!) " + tc.status.capitalize()
            error_msg = tc.error_message[:200] if tc.error_message else "—"
            cases_table += f"| {i} | {tc.name} | {status_icon} | {tc.duration} | {error_msg} |\n"
        
        # Logs section
        logs_section = (
            f"\nh3. Execution Logs\n"
            f"{{code:title=Full Output|collapse=true}}\n"
            f"{results.logs[:2000]}\n"
            f"{{code}}\n"
        )
        
        return header + cases_table + logs_section

    async def run(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"CommitAgent posting results for: {state.request.jira_id}")
        state.logs.append(f"CommitAgent: Posting results to Jira {state.request.jira_id}...")
        
        issue_key = state.request.jira_id
        
        try:
            comment = self._build_results_table(state)
            await asyncio.to_thread(jira_comment_tool.post_comment, issue_key, comment)
            
            # Attach generated script
            if state.generated_script_path:
                await asyncio.to_thread(jira_comment_tool.attach_file, issue_key, state.generated_script_path)
                
            state.logs.append("CommitAgent: Jira updated successfully with test results table")
        except Exception as e:
            logger.error(f"CommitAgent failed: {e}")
            state.logs.append(f"CommitAgent Error: {str(e)}")
            
        return state

commit_agent = CommitAgent()
