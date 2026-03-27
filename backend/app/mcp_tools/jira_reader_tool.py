from jira import JIRA
from config.settings import settings
from utils.logger import logger
from schemas.request_schema import JiraContext

class JiraReaderTool:
    def __init__(self):
        self._jira = None

    @property
    def jira(self):
        if self._jira is None:
            self._jira = JIRA(
                server=settings.JIRA_BASE_URL,
                basic_auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
            )
        return self._jira

    def fetch_issue(self, issue_key: str) -> JiraContext:
        try:
            logger.info(f"Fetching Jira issue: {issue_key}")
            
            # Diagnostic: Verify connection
            myself = self.jira.myself()
            logger.info(f"Connected to Jira as: {myself.get('displayName')} ({myself.get('emailAddress')})")
            
            issue = self.jira.issue(issue_key)
            
            # Simple extraction logic
            summary = issue.fields.summary
            description = issue.fields.description or ""
            
            # Placeholder for complex parsing of AC and Steps
            # In a real scenario, we might use LLM to parse raw description
            ac = []
            steps = []
            
            if "Acceptance Criteria" in description:
                ac_part = description.split("Acceptance Criteria")[1].split("Steps to Reproduce")[0]
                ac = [line.strip("- *") for line in ac_part.strip().split("\n") if line.strip()]
            
            if "Steps to Reproduce" in description:
                steps_part = description.split("Steps to Reproduce")[1]
                steps = [line.strip("1234567890. ") for line in steps_part.strip().split("\n") if line.strip()]

            return JiraContext(
                summary=summary,
                description=description,
                acceptance_criteria=ac,
                steps=steps,
                issue_type=getattr(issue.fields, 'issuetype', {}).name if hasattr(issue.fields, 'issuetype') and issue.fields.issuetype else None,
                priority=getattr(issue.fields, 'priority', {}).name if hasattr(issue.fields, 'priority') and issue.fields.priority else None,
                status=getattr(issue.fields, 'status', {}).name if hasattr(issue.fields, 'status') and issue.fields.status else None,
                labels=getattr(issue.fields, 'labels', []),
                components=[comp.name for comp in getattr(issue.fields, 'components', [])] if hasattr(issue.fields, 'components') and issue.fields.components else [],
                reporter=getattr(issue.fields, 'reporter', {}).displayName if hasattr(issue.fields, 'reporter') and issue.fields.reporter else None,
                assignee=getattr(issue.fields, 'assignee', {}).displayName if hasattr(issue.fields, 'assignee') and issue.fields.assignee else None,
                created=str(getattr(issue.fields, 'created', '')) if hasattr(issue.fields, 'created') else None,
                updated=str(getattr(issue.fields, 'updated', '')) if hasattr(issue.fields, 'updated') else None,
                url=self.jira.server_url + "/browse/" + issue_key  # Add URL field
            )
        except Exception as e:
            logger.error(f"Error fetching Jira issue {issue_key}: {e}")
            if "401" in str(e):
                logger.error(f"AUTHENTICATION FAILURE: Please check if JIRA_API_TOKEN for {settings.JIRA_EMAIL} is valid for {settings.JIRA_BASE_URL}")
                logger.error("Verify that the token was generated at https://id.atlassian.com/manage-profile/security/api-tokens")
            raise e

jira_reader_tool = JiraReaderTool()
