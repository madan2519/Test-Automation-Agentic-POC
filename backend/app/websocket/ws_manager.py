from fastapi import WebSocket
from typing import List, Dict
import json
import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", ".cache")
RESULTS_CACHE_FILE = os.path.join(CACHE_DIR, "results_cache.json")
LOGS_CACHE_FILE = os.path.join(CACHE_DIR, "logs_cache.json")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # Load persistent cache from disk
        self.results_cache: Dict[str, dict] = self._load_cache(RESULTS_CACHE_FILE)
        self.logs_cache: Dict[str, List[dict]] = self._load_cache(LOGS_CACHE_FILE)

    def _load_cache(self, filepath: str) -> dict:
        """Load cache from a JSON file on disk."""
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_results_cache(self):
        """Persist results cache to disk."""
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(RESULTS_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.results_cache, f)
        except Exception:
            pass

    def _save_logs_cache(self):
        """Persist logs cache to disk."""
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(LOGS_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.logs_cache, f)
        except Exception:
            pass

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

    async def send_log(self, event: str, data: dict):
        # Update cache based on event type
        jira_id = data.get("jira_id")
        
        if jira_id:
            if event == "agent_update":
                if jira_id not in self.logs_cache:
                    self.logs_cache[jira_id] = []
                self.logs_cache[jira_id].append(data)
                self._save_logs_cache()
            
            if event in ("execution_finished", "workflow_finished"):
                self.results_cache[jira_id] = data
                self._save_results_cache()

        message = json.dumps({"event": event, "data": data})
        await self.broadcast(message)

    def get_session_data(self, jira_id: str):
        """Retrieve cached logs and results for recovery."""
        return {
            "logs": self.logs_cache.get(jira_id, []),
            "result": self.results_cache.get(jira_id)
        }

manager = ConnectionManager()
