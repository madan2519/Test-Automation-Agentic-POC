from mcp_tools.jira_reader_tool import jira_reader_tool
from schemas.request_schema import WorkflowState
from utils.logger import logger

class JiraAgent:
    async def run(self, state: WorkflowState) -> WorkflowState:
        logger.info(f"JiraAgent fetching details for: {state.request.jira_id}")
        state.logs.append(f"JiraAgent: Fetching ticket {state.request.jira_id}")
        
        try:
            import asyncio
            # Add timeout to prevent hanging (30 seconds)
            jira_data = await asyncio.wait_for(
                asyncio.to_thread(jira_reader_tool.fetch_issue, state.request.jira_id),
                timeout=30.0
            )
            state.jira_data = jira_data
            state.logs.append(f"JiraAgent: Successfully fetched ticket data")
        except asyncio.TimeoutError:
            logger.error(f"JiraAgent timeout for {state.request.jira_id}")
            state.logs.append(f"JiraAgent Error: Timeout fetching ticket {state.request.jira_id}")
            state.jira_data = None
            state.logs.append("JiraAgent: Aborting workflow due to timeout")
        except Exception as e:
            logger.error(f"JiraAgent failed for {state.request.jira_id}: {e}")
            if "404" in str(e):
                state.logs.append(f"JiraAgent Error: Ticket {state.request.jira_id} not found.")
            elif "401" in str(e):
                state.logs.append("JiraAgent Error: Authentication failed. Check API Token.")
            else:
                state.logs.append(f"JiraAgent Error: {str(e)}")
            
            state.jira_data = None
            state.logs.append("JiraAgent: Aborting workflow due to missing ticket data")
            
        return state

jira_agent = JiraAgent()
