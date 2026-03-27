from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from schemas.request_schema import WorkflowState
from agents.jira_agent import jira_agent
from agents.test_plan_agent import test_plan_agent
from agents.orchestrator_agent import orchestrator_agent
from agents.script_generators.python_playwright_agent import python_playwright_agent
from agents.script_generators.python_selenium_agent import python_selenium_agent
from agents.script_generators.java_selenium_agent import java_selenium_agent
from agents.script_generators.python_appium_agent import python_appium_agent
from agents.executors.playwright_executor import playwright_executor
from agents.executors.selenium_executor import selenium_executor
from agents.executors.appium_executor import appium_executor
from agents.executors.robot_executor import robot_executor
from agents.retry_agent import retry_agent
from agents.commit_agent import commit_agent
from utils.logger import logger

def create_workflow():
    workflow = StateGraph(WorkflowState)

    # Define nodes - mapping functions to node names
    workflow.add_node("jira_agent", jira_agent.run)
    workflow.add_node("test_plan_agent", test_plan_agent.run)
    workflow.add_node("orchestrator", orchestrator_agent.run)
    workflow.add_node("script_generator", python_playwright_agent.run)
    workflow.add_node("selenium_script_generator", python_selenium_agent.run)
    workflow.add_node("java_selenium_generator", java_selenium_agent.run)
    workflow.add_node("appium_script_generator", python_appium_agent.run)
    workflow.add_node("executor", playwright_executor.run)
    workflow.add_node("selenium_executor", selenium_executor.run)
    workflow.add_node("appium_executor", appium_executor.run)
    workflow.add_node("robot_executor", robot_executor.run)
    workflow.add_node("retry_agent", retry_agent.run)
    workflow.add_node("commit_agent", commit_agent.run)


    # Build graph
    workflow.set_entry_point("jira_agent")
    workflow.add_edge("jira_agent", "test_plan_agent")  # Direct to combined agent
    workflow.add_edge("test_plan_agent", "orchestrator")
    
    # Routing from orchestrator to generators
    def route_to_generator(state: WorkflowState):
        if state.generator_name == "python_selenium_agent":
            return "selenium_script_generator"
        if state.generator_name == "java_selenium_agent":
            return "java_selenium_generator"
        if state.generator_name == "python_appium_agent":
            return "appium_script_generator"
        return "script_generator"

    workflow.add_conditional_edges(
        "orchestrator",
        route_to_generator,
        {
            "selenium_script_generator": "selenium_script_generator",
            "java_selenium_generator": "java_selenium_generator",
            "appium_script_generator": "appium_script_generator",
            "script_generator": "script_generator"
        }
    )

    # Routing from generators to executors
    workflow.add_edge("script_generator", "executor")  # python_playwright_agent → playwright_executor
    workflow.add_edge("selenium_script_generator", "selenium_executor")
    workflow.add_edge("java_selenium_generator", "selenium_executor")
    workflow.add_edge("appium_script_generator", "appium_executor")
    
    # Special routing for Robot Framework - python_playwright_agent should go to robot_executor
    def route_to_executor(state: WorkflowState):
        if state.executor_name == "robot_executor":
            return "robot_executor"
        if state.executor_name == "selenium_executor":
            return "selenium_executor"
        if state.executor_name == "appium_executor":
            return "appium_executor"
        return "executor"  # default to playwright_executor
    
    workflow.add_conditional_edges(
        "script_generator",
        route_to_executor,
        {
            "robot_executor": "robot_executor",
            "selenium_executor": "selenium_executor", 
            "appium_executor": "appium_executor",
            "executor": "executor"
        }
    )
    
    # All executors go to retry_agent
    workflow.add_edge("executor", "retry_agent")
    workflow.add_edge("selenium_executor", "retry_agent")
    workflow.add_edge("appium_executor", "retry_agent")
    workflow.add_edge("robot_executor", "retry_agent")

    # Conditional edge for retry logic
    def should_retry(state: WorkflowState):
        if state.execution_results and state.execution_results.failed > 0 and state.retry_count < 3:
            if state.executor_name == "selenium_executor":
                return "selenium_executor"
            if state.executor_name == "appium_executor":
                return "appium_executor"
            if state.executor_name == "robot_executor":
                return "robot_executor"
            return "executor"  # default to playwright_executor
        return "commit_agent"

    workflow.add_conditional_edges(
        "retry_agent",
        should_retry,
        {
            "executor": "executor",
            "selenium_executor": "selenium_executor",
            "appium_executor": "appium_executor",
            "robot_executor": "robot_executor",
            "commit_agent": "commit_agent"
        }
    )

    workflow.add_edge("commit_agent", END)

    compiled = workflow.compile()
    
    # Comment out automatic graph generation to avoid startup issues
    # png_bytes = compiled.get_graph().draw_mermaid_png()
    # with open("graph_flow_mermaid.png", "wb") as f:
    #     f.write(png_bytes)

    return compiled

app_graph = create_workflow()
