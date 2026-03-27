import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from schemas.request_schema import AutomationRequest, WorkflowState
from graph.workflow_graph import app_graph
from websocket.ws_manager import manager
from utils.logger import logger

app = FastAPI(title="AI Automation Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Automation Platform Backend is running"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            text = await websocket.receive_text()
            try:
                msg = json.loads(text)
                if msg.get("event") == "ping":
                    await websocket.send_text(json.dumps({"event": "pong", "data": {}}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def run_workflow(request: AutomationRequest):
    try:
        logger.info(f"Starting workflow for {request.jira_id}")
        full_state = WorkflowState(request=request)
        
        # We use stream to get node updates for logs
        async for output in app_graph.astream(full_state):
            for node_name, state_update in output.items():
                logger.info(f"--- Entering Node: {node_name} ---")
                logger.debug(f"Node {node_name} update received")
                
                # Accumulate state - merged with full_state
                if isinstance(state_update, dict):
                    # Partial update from LangGraph
                    for key, val in state_update.items():
                        if hasattr(full_state, key):
                            # Skip updating the request field to avoid LangGraph state conflicts
                            if key != 'request':
                                setattr(full_state, key, val)
                elif isinstance(state_update, WorkflowState):
                    # Full object update (fallback)
                    full_state = state_update

                # Helper to get field from state_update (could be dict or object)
                def get_field(obj, field):
                    if isinstance(obj, dict):
                        return obj.get(field)
                    try:
                        return getattr(obj, field, None)
                    except Exception:
                        return None
                
                logs = get_field(state_update, "logs") or []
                jira_data_obj = get_field(state_update, "jira_data")
                
                latest_log = logs[-1] if logs else f"Current node: {node_name}"
                
                # Convert Pydantic model to dict if needed
                jira_data_dict = None
                if jira_data_obj:
                    jira_data_dict = jira_data_obj.model_dump() if hasattr(jira_data_obj, "model_dump") else jira_data_obj

                logger.debug(f"Sending update for {node_name} with jira_data: {jira_data_dict is not None}")
                
                await manager.send_log("agent_update", {
                    "node": node_name,
                    "msg": latest_log,
                    "jira_id": request.jira_id,
                    "jira_data": jira_data_dict
                })
                
                # If execution finished in this update, send results
                results = get_field(state_update, "execution_results")
                if results:
                    # Handle both Pydantic model and dict
                    results_dict = results.model_dump() if hasattr(results, "model_dump") else results
                    results_dict["jira_id"] = request.jira_id
                    await manager.send_log("execution_finished", results_dict)
                
                if node_name == "commit_agent":
                    # Send final workflow finished with all relevant final data
                    try:
                        results_final = full_state.execution_results.model_dump() if full_state.execution_results else None
                        jira_final = full_state.jira_data.model_dump() if full_state.jira_data else None
                        
                        await manager.send_log("workflow_finished", {
                            "status": "success",
                            "execution_results": results_final,
                            "jira_data": jira_final
                        })
                        logger.info(f"Workflow for {request.jira_id} finished successfully")
                    except Exception as dump_err:
                        logger.error(f"Error dumping final state: {dump_err}")
                        await manager.send_log("workflow_finished", {
                            "status": "partial_success",
                            "msg": "Workflow finished but state serialization failed"
                        })
    except Exception as e:
        logger.error(f"Error in run_workflow: {e}", exc_info=True)
        # Ensure we send a failure flag to the cache
        error_data = {
            "node": "error",
            "msg": f"Workflow failed: {str(e)}",
            "jira_id": request.jira_id
        }
        await manager.send_log("agent_update", error_data)
        
@app.get("/automation-status/{jira_id}")
async def get_automation_status(jira_id: str):
    logger.info(f"Retrieving session data for {jira_id}")
    return manager.get_session_data(jira_id)

@app.post("/start-automation")
async def start_automation(request: AutomationRequest, background_tasks: BackgroundTasks):
    logger.info(f"Received automation request for {request.jira_id}")
    background_tasks.add_task(run_workflow, request)
    return {"status": "started", "jira_id": request.jira_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
