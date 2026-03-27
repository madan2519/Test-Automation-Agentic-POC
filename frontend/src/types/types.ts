export interface AutomationRequest {
  jira_id: string;
  platform: string;
  language: string;
  framework: string;
  browser?: string;
  device?: string;
  environment: string;
}

export interface JiraContext {
  summary: string;
  description: string;
  acceptance_criteria: string[];
  steps: string[];
}

export interface AgentLog {
  node: string;
  msg: string;
  jira_id: string;
  timestamp: string;
  jira_data?: JiraContext;
}

export interface TestCaseResult {
  name: string;
  status: string;
  duration: string;
  error_message: string;
}

export interface ExecutionResult {
  tests_run: number;
  passed: number;
  failed: number;
  execution_time: string;
  test_cases: TestCaseResult[];
  logs: string;
}

export type WorkflowStatus = 'idle' | 'running' | 'success' | 'failed';

