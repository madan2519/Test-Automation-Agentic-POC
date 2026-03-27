from jira import JIRA
import os
from config.settings import settings
from utils.logger import logger

class JiraCommentTool:
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

    def post_comment(self, issue_key: str, comment: str):
        try:
            logger.info(f"Posting comment to Jira issue: {issue_key}")
            self.jira.add_comment(issue_key, comment)
        except Exception as e:
            logger.error(f"Error posting comment to Jira {issue_key}: {e}")
            raise e

    def attach_file(self, issue_key: str, file_path: str):
        try:
            logger.info(f"Attaching file to Jira issue: {issue_key} - {file_path}")
            if os.path.exists(file_path):
                self.jira.add_attachment(issue_key, file_path)
        except Exception as e:
            logger.error(f"Error attaching file to Jira {issue_key}: {e}")
            # Non-critical failure
            pass

jira_comment_tool = JiraCommentTool()
