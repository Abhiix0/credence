import logging
import os
import time
from typing import Dict, List, Optional, Set, Tuple
from dotenv import load_dotenv

from ..models import Agent, Reputation, Task, TaskStatus
from ..policies import (
    BasePolicy,
    ConservativePolicy,
    AggressivePolicy,
    ReputationPolicy,
    BalancedPolicy,
)
from ..wallet import WalletSigner
from ..market import TaskMarketClient
from ..execution import TaskExecutor

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AutonomousAgent")


POLICY_REGISTRY: Dict[str, BasePolicy] = {
    "ConservativePolicy": ConservativePolicy(),
    "AggressivePolicy": AggressivePolicy(),
    "ReputationPolicy": ReputationPolicy(),
    "BalancedPolicy": BalancedPolicy(),
}


class AutonomousAgent:
    """
    Autonomous AI Agent executing on Monad testnet.
    
    Full Loop Lifecycle:
    1. Observe (update balance)
    2. Discover open tasks → Evaluate → Bid
    3. Discover assigned tasks (mine) → Execute → Submit results
    
    The agent now handles both bidding on new tasks AND executing assigned tasks.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        policy_name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ):
        self.signer = WalletSigner()
        self.market = TaskMarketClient(self.signer)
        self.executor = TaskExecutor()

        policy_key = policy_name or os.getenv("AGENT_POLICY", "ConservativePolicy")
        self.policy = POLICY_REGISTRY.get(policy_key, ConservativePolicy())
        
        caps_str = os.getenv("AGENT_CAPABILITIES", "text-processing,data-analysis,code-review")
        caps_list = capabilities or [c.strip() for c in caps_str.split(",") if c.strip()]

        self.agent_state = Agent(
            wallet_address=self.signer.address,
            name=name or os.getenv("AGENT_NAME", "MonadAgent-01"),
            balance_wei=self.signer.get_balance(),
            capabilities=caps_list,
            reputation=Reputation(agent_address=self.signer.address),
            policy_name=self.policy.name,
            is_active=True,
        )
        
        # Track tasks currently being processed to avoid double execution
        self._in_progress: Set[int] = set()
        # Track tasks already submitted to avoid resubmission
        self._submitted: Set[int] = set()

        logger.info(f"Agent initialized: {self.agent_state.name} [{self.agent_state.wallet_address}]")
        logger.info(f"Active Policy: {self.policy.name}, Capabilities: {self.agent_state.capabilities}")

    def observe(self) -> None:
        """Observe environment: update balance and network connectivity."""
        self.agent_state.balance_wei = self.signer.get_balance()
        logger.info(f"[Observe] Balance: {self.agent_state.balance_wei} wei")

    def discover(self) -> List[Task]:
        """Discover available open tasks on Monad TaskMarket."""
        open_tasks = self.market.fetch_open_tasks()
        logger.info(f"[Discover] Found {len(open_tasks)} open tasks on market")
        return open_tasks

    def discover_assigned_tasks(self) -> List[Task]:
        """
        Discover tasks assigned to this agent (me as the selected worker).
        
        Filters for:
        - task.status == TaskStatus.ASSIGNED
        - task.selected_worker == self.signer.address (case-insensitive)
        
        Returns:
            List of tasks assigned to this agent
        """
        if not self.market.contract:
            return []
        
        try:
            total = self.market.contract.functions.totalTasks().call()
            my_assigned_tasks = []
            
            my_address = self.signer.address.lower()
            
            for task_id in range(1, total + 1):
                raw = self.market.contract.functions.getTask(task_id).call()
                
                # Status 1 = Assigned
                if raw[6] == 1:
                    selected_worker = raw[7]
                    
                    # Check if I'm the selected worker (case-insensitive)
                    if selected_worker.lower() == my_address:
                        task = Task(
                            task_id=raw[0],
                            creator=raw[1],
                            specification_uri=raw[2],
                            required_capability=raw[3],
                            reward_wei=raw[4],
                            deadline=raw[5],
                            status=TaskStatus.ASSIGNED,
                            selected_worker=raw[7],
                            accepted_bid_id=raw[8] if raw[8] > 0 else None,
                            result_uri=raw[9],
                            result_hash=raw[10],
                        )
                        my_assigned_tasks.append(task)
            
            logger.info(f"[Discover Assigned] Found {len(my_assigned_tasks)} tasks assigned to me")
            return my_assigned_tasks
            
        except Exception as e:
            logger.error(f"Error discovering assigned tasks: {e}")
            return []

    def evaluate_and_decide(self, task: Task) -> Optional[dict]:
        """Evaluate task through policy and decide bidding action."""
        should_bid, price, duration = self.policy.evaluate(self.agent_state, task)
        if should_bid and price and duration:
            logger.info(f"[Decide] Policy accepted Task #{task.task_id} @ {price} wei (duration: {duration}s)")
            return {
                "task_id": task.task_id,
                "proposed_price": price,
                "estimated_duration": duration,
            }
        logger.info(f"[Decide] Policy skipped Task #{task.task_id}")
        return None

    def sign_and_submit_bid(self, decision: dict) -> Optional[str]:
        """Sign and broadcast bid transaction to Monad testnet."""
        logger.info(f"[Sign Tx] Signing bid for Task #{decision['task_id']}")
        return self.market.submit_bid(
            task_id=decision["task_id"],
            proposed_price=decision["proposed_price"],
            estimated_duration=decision["estimated_duration"],
        )

    def execute_task(self, task: Task) -> Tuple[str, bytes]:
        """Execute task work payload via TaskExecutor."""
        logger.info(f"[Execute] Executing work for Task #{task.task_id}")
        return self.executor.execute(task)

    def submit_result(self, task_id: int, result_uri: str, result_hash: bytes) -> Optional[str]:
        """Submit execution proof on-chain."""
        logger.info(f"[Submit Result] Posting proof for Task #{task_id} -> {result_uri}")
        return self.market.submit_task_result(task_id, result_uri, result_hash)

    def run_worker_cycle(self) -> None:
        """
        Worker cycle: execute and submit results for assigned tasks.
        
        For each task assigned to me:
        1. Check if not already in progress or submitted
        2. Mark as in-progress to avoid double execution
        3. Execute task to generate result
        4. Submit result to blockchain
        5. Mark as submitted on success
        
        This is idempotent and safe against re-running on already-submitted tasks.
        """
        # Discover tasks assigned to me
        assigned_tasks = self.discover_assigned_tasks()
        
        if not assigned_tasks:
            logger.debug("No tasks currently assigned to me")
            return
        
        for task in assigned_tasks:
            # Skip if already processed or in progress
            if task.task_id in self._submitted:
                logger.debug(f"Task #{task.task_id} already submitted, skipping")
                continue
            
            if task.task_id in self._in_progress:
                logger.debug(f"Task #{task.task_id} already in progress, skipping")
                continue
            
            try:
                # Mark as in progress
                self._in_progress.add(task.task_id)
                logger.info(f"[Worker Cycle] Processing assigned Task #{task.task_id}")
                
                # Execute task
                result_uri, result_hash = self.execute_task(task)
                
                # Submit result
                tx_hash = self.submit_result(task.task_id, result_uri, result_hash)
                
                if tx_hash:
                    logger.info(f"Result submitted successfully: tx {tx_hash}")
                    # Mark as submitted
                    self._submitted.add(task.task_id)
                else:
                    logger.error(f"Failed to submit result for Task #{task.task_id}")
                
            except Exception as e:
                logger.error(f"Error processing Task #{task.task_id}: {e}")
            
            finally:
                # Remove from in-progress (whether success or failure)
                # This allows retry on next cycle if submission failed
                if task.task_id in self._in_progress:
                    self._in_progress.discard(task.task_id)

    def step(self) -> None:
        """
        Execute a single step of the autonomous loop.
        
        Full per-tick order:
        1. Observe (update balance)
        2. Discover open tasks → Evaluate → Bid
        3. Discover assigned tasks (mine) → Execute → Submit results
        """
        # 1. Observe
        self.observe()

        # 2. Discover open tasks and bid
        open_tasks = self.discover()
        for task in open_tasks:
            decision = self.evaluate_and_decide(task)
            if decision:
                tx_hash = self.sign_and_submit_bid(decision)
                if tx_hash:
                    logger.info(f"Bid confirmed: tx {tx_hash}")

        # 3. Discover assigned tasks and execute
        self.run_worker_cycle()

    def run_forever(self, interval_seconds: int = 15) -> None:
        """Continuously loop agent lifecycle."""
        logger.info("Starting Autonomous Agent loop...")
        logger.info("Agent will bid on open tasks AND execute assigned tasks")
        while self.agent_state.is_active:
            try:
                self.step()
            except Exception as e:
                logger.error(f"Error in agent cycle: {e}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    agent = AutonomousAgent()
    agent.step()

