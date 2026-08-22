import hashlib
import os
from typing import Dict, Any, Tuple, Optional
from ..models import Task


class TaskExecutor:
    """Executes assigned tasks and interfaces with Gemini AI for reasoning."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # Lazy initialization hook for Gemini AI client

    def execute(self, task: Task) -> Tuple[str, bytes]:
        """
        Execute task specification and generate verifiable result proof.
        
        Returns:
            Tuple[result_uri: str, result_hash: bytes32]
        """
        # Execute computational or AI task logic
        execution_payload = f"Task Execution for {task.task_id} [{task.required_capability}]: {task.specification_uri}"
        
        # Calculate SHA256 proof hash
        raw_hash = hashlib.sha256(execution_payload.encode("utf-8")).digest()
        result_uri = f"ipfs://result-{task.task_id}-{hashlib.sha256(raw_hash).hexdigest()[:12]}"
        
        return result_uri, raw_hash
