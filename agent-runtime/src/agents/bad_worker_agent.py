"""
BadWorkerAgent - Intentionally produces incorrect results for testing verification.

This agent is used to test and demonstrate the verification system's ability to
detect and penalize fraudulent or low-quality work. It:

1. Bids aggressively on all matching tasks (ignores price sensibility)
2. Produces deliberately wrong results ~40% of the time (configurable)
3. Uses identical on-chain transaction plumbing as honest workers
4. Allows VerifierAgent to genuinely catch and penalize bad work

IMPORTANT: This is for testing/demo purposes only. Do not use in production.
"""

import hashlib
import json
import logging
import os
import random
from typing import Optional, Tuple
from dotenv import load_dotenv

from ..models import Agent, Task, TaskStatus
from .base_agent import AutonomousAgent
from ..logging_utils import log_bid_decision

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BadWorkerAgent")


class BadWorkerAgent(AutonomousAgent):
    """
    Bad worker agent that intentionally produces incorrect results.
    
    Overrides:
    - Policy evaluation: Always bid on matching capabilities (aggressive)
    - Task execution: Returns wrong results based on failure rate
    
    On-chain interaction is identical to honest workers, so verification
    catches the fraud through result hash comparison.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        policy_name: Optional[str] = None,
        capabilities: Optional[list[str]] = None,
        failure_rate: Optional[float] = None,
    ):
        """
        Initialize BadWorkerAgent.
        
        Args:
            name: Agent name (defaults to env AGENT_NAME or "BadWorker-01")
            policy_name: Ignored - always uses aggressive bidding
            capabilities: Agent capabilities
            failure_rate: Probability of producing bad result (0.0-1.0, default 0.4)
        """
        # Initialize parent (AutonomousAgent)
        super().__init__(name=name, policy_name=policy_name, capabilities=capabilities)
        
        # Override name if not explicitly set
        if name is None and "AGENT_NAME" not in os.environ:
            self.agent_state.name = "BadWorker-01"
        
        # Configure failure rate
        self.failure_rate = failure_rate or float(os.getenv("AGENT_FAILURE_RATE", "0.4"))
        
        # Seed RNG for reproducibility (optional)
        seed = os.getenv("AGENT_FAILURE_SEED")
        if seed:
            random.seed(int(seed))
        
        logger.warning("="*70)
        logger.warning("⚠️  BAD WORKER AGENT INITIALIZED ⚠️")
        logger.warning("="*70)
        logger.warning(f"Agent: {self.agent_state.name}")
        logger.warning(f"Failure Rate: {self.failure_rate * 100:.1f}% of tasks will produce bad results")
        logger.warning("This agent is for testing verification systems only!")
        logger.warning("="*70)

    def evaluate_and_decide(self, task: Task) -> Optional[dict]:
        """
        Override policy evaluation: Always bid on matching capabilities.
        
        Ignores price sensibility and always bids aggressively on tasks
        where we have the required capability.
        
        Args:
            task: Task to evaluate
            
        Returns:
            Bid decision dict, or None if capability doesn't match
        """
        if task.status != TaskStatus.OPEN:
            return None
        
        # Check if we have the required capability
        if task.required_capability not in self.agent_state.capabilities:
            logger.info(f"[Decide] Skipping Task #{task.task_id} - capability mismatch")
            return None
        
        # Always bid aggressively (low price, fast delivery)
        proposed_price = max(int(task.reward_wei * 0.5), 1)  # 50% of reward
        estimated_duration = 300  # 5 minutes
        
        # Use standardized logging
        log_bid_decision(
            agent_name=self.agent_state.name,
            task_id=task.task_id,
            task_capability=task.required_capability,
            task_reward_wei=task.reward_wei,
            policy_name="AggressiveBad",
            decision="BID",
            proposed_price_wei=proposed_price,
            estimated_duration_sec=estimated_duration,
            reason="Bad worker always bids aggressively at 50% reward with fast delivery promise"
        )
        
        return {
            "task_id": task.task_id,
            "proposed_price": proposed_price,
            "estimated_duration": estimated_duration,
        }

    def execute_task(self, task: Task) -> Tuple[str, bytes]:
        """
        Override task execution: Produce bad results based on failure rate.
        
        With probability = failure_rate, returns deliberately wrong result:
        - sentiment-analysis: Always "positive" regardless of input
        - classification: Always first category regardless of content
        - Other tasks: Malformed JSON
        
        With probability = (1 - failure_rate), calls real executor (honest work).
        
        Args:
            task: Task to execute
            
        Returns:
            Tuple[result_uri, result_hash] - may be fraudulent
        """
        # Decide whether to produce bad result
        produce_bad_result = random.random() < self.failure_rate
        
        if produce_bad_result:
            logger.warning(f"[Execute] ⚠️  Producing BAD result for Task #{task.task_id}")
            return self._execute_bad(task)
        else:
            logger.info(f"[Execute] Producing honest result for Task #{task.task_id}")
            return super().execute_task(task)  # Call real executor

    def _execute_bad(self, task: Task) -> Tuple[str, bytes]:
        """
        Produce deliberately wrong result for testing verification.
        
        Args:
            task: Task to execute (incorrectly)
            
        Returns:
            Tuple[result_uri, result_hash] with wrong result
        """
        capability = task.required_capability.lower().strip()
        
        # Generate wrong result based on capability
        if capability == "sentiment-analysis":
            # Always return "positive" regardless of input
            wrong_output = json.dumps({"result": "positive"})
            logger.warning(f"  → Fraudulent sentiment: always 'positive'")
        
        elif capability == "classification":
            # Always return first category or generic label
            wrong_output = json.dumps({"result": "general"})
            logger.warning(f"  → Fraudulent classification: always 'general'")
        
        else:
            # Generic malformed result for unknown capabilities
            wrong_output = json.dumps({
                "result": "fraudulent_output",
                "error": "This is a deliberately bad result for testing"
            })
            logger.warning(f"  → Fraudulent generic result")
        
        # Hash the WRONG output (just like honest worker would)
        result_hash = hashlib.sha256(wrong_output.encode("utf-8")).digest()
        
        # Build result URI (same format as honest worker)
        hash_hex = result_hash.hex()
        result_uri = f"ipfs://result-{task.task_id}-{hash_hex[:12]}"
        
        logger.warning(f"  → Bad result hash: {hash_hex}")
        logger.warning(f"  → This WILL FAIL verification ❌")
        
        return result_uri, result_hash


if __name__ == "__main__":
    """
    Standalone bad worker agent execution.
    
    Environment variables:
    - AGENT_NAME: Agent name (default: "BadWorker-01")
    - AGENT_PRIVATE_KEY: Private key
    - AGENT_CAPABILITIES: Comma-separated capabilities
    - AGENT_FAILURE_RATE: Probability of bad result (0.0-1.0, default 0.4)
    - AGENT_FAILURE_SEED: Optional RNG seed for reproducibility
    """
    logger.warning("\n" + "="*70)
    logger.warning("STARTING BAD WORKER AGENT")
    logger.warning("This agent will intentionally produce incorrect results!")
    logger.warning("="*70 + "\n")
    
    agent = BadWorkerAgent()
    
    # Run one cycle for testing
    agent.step()
    
    # Uncomment to run continuously:
    # agent.run_forever(interval_seconds=15)
