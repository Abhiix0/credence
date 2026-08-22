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
from ..logging_utils import log_bid_decision, log_reputation_change

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
            reputation=Reputation(
                agent_address=self.signer.address,
                simulated_stake_wei=int(os.getenv("AGENT_SIMULATED_STAKE_WEI", "1000000000000000000"))  # 1 ETH default
            ),
            policy_name=self.policy.name,
            is_active=True,
        )
        
        # Track tasks currently being processed to avoid double execution
        self._in_progress: Set[int] = set()
        # Track tasks already submitted to avoid resubmission
        self._submitted: Set[int] = set()
        # Task snapshots for lightweight event polling
        self._task_snapshots: Dict[int, TaskStatus] = {}

        logger.info(f"Agent initialized: {self.agent_state.name} [{self.agent_state.wallet_address}]")
        logger.info(f"Active Policy: {self.policy.name}, Capabilities: {self.agent_state.capabilities}")
        logger.info(f"Simulated Stake: {self.agent_state.reputation.simulated_stake_wei} wei")

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
            # Use standardized logging for bid decision
            log_bid_decision(
                agent_name=self.agent_state.name,
                task_id=task.task_id,
                task_capability=task.required_capability,
                task_reward_wei=task.reward_wei,
                policy_name=self.policy.name,
                decision="BID",
                proposed_price_wei=price,
                estimated_duration_sec=duration,
                reason=f"Policy accepted task based on capability match and reward threshold"
            )
            return {
                "task_id": task.task_id,
                "proposed_price": price,
                "estimated_duration": duration,
            }
        
        # Log skip decision (optional, less verbose)
        logger.debug(f"[Decide] Policy skipped Task #{task.task_id}")
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
        
        # 4. Poll for task settlements and update local reputation
        self.poll_my_task_settlements()

    def poll_my_task_settlements(self) -> None:
        """
        Poll for settlements on tasks I worked on and update local reputation.
        
        Tracks tasks transitioning to VERIFIED_PASS/VERIFIED_FAIL and updates
        local reputation tracking (completed_tasks, failed_tasks, score, stake).
        """
        if not self.market.contract:
            return
        
        try:
            total = self.market.contract.functions.totalTasks().call()
            my_address = self.signer.address.lower()
            
            for task_id in range(1, total + 1):
                raw = self.market.contract.functions.getTask(task_id).call()
                
                # Only track tasks I worked on
                selected_worker = raw[7]
                if not selected_worker or selected_worker.lower() != my_address:
                    continue
                
                current_status = TaskStatus(raw[6])
                old_status = self._task_snapshots.get(task_id)
                
                # Detect settlement (transition to VERIFIED_PASS or VERIFIED_FAIL)
                if old_status is not None and old_status != current_status:
                    if current_status == TaskStatus.VERIFIED_PASS:
                        self._handle_task_pass(task_id, raw[4])  # reward_wei
                        logger.info(f"[Settlement] Task #{task_id} PASSED ✅")
                    elif current_status == TaskStatus.VERIFIED_FAIL:
                        self._handle_task_fail(task_id, raw[4])  # reward_wei
                        logger.info(f"[Settlement] Task #{task_id} FAILED ❌")
                
                # Update snapshot
                self._task_snapshots[task_id] = current_status
                
        except Exception as e:
            logger.error(f"Error polling task settlements: {e}")

    def _handle_task_pass(self, task_id: int, reward_wei: int) -> None:
        """
        Handle successful task completion: update local reputation.
        
        Args:
            task_id: Task that passed verification
            reward_wei: Task reward amount
        """
        old_score = self.agent_state.reputation.score
        old_completed = self.agent_state.reputation.completed_tasks
        old_failed = self.agent_state.reputation.failed_tasks
        
        # Update reputation
        self.agent_state.reputation.completed_tasks += 1
        score_increase = 2
        self.agent_state.reputation.score = min(100, self.agent_state.reputation.score + score_increase)
        
        # Use standardized logging
        log_reputation_change(
            agent_name=self.agent_state.name,
            worker_address=self.agent_state.wallet_address,
            task_id=task_id,
            change_type="Task Pass",
            old_score=old_score,
            new_score=self.agent_state.reputation.score,
            old_completed=old_completed,
            new_completed=self.agent_state.reputation.completed_tasks,
            old_failed=old_failed,
            new_failed=self.agent_state.reputation.failed_tasks,
            stake_change_wei=0,
            reason="Task completed successfully and verified"
        )

    def _handle_task_fail(self, task_id: int, reward_wei: int) -> None:
        """
        Handle failed task: update local reputation and simulate stake slash.
        
        Args:
            task_id: Task that failed verification
            reward_wei: Task reward amount (used to calculate slash)
        """
        old_score = self.agent_state.reputation.score
        old_completed = self.agent_state.reputation.completed_tasks
        old_failed = self.agent_state.reputation.failed_tasks
        old_stake = self.agent_state.reputation.simulated_stake_wei
        
        # Update reputation
        self.agent_state.reputation.failed_tasks += 1
        score_decrease = 10
        self.agent_state.reputation.score = max(0, self.agent_state.reputation.score - score_decrease)
        
        # Simulate stake slash (10% of reward, up to available stake)
        slash_amount = min(self.agent_state.reputation.simulated_stake_wei, reward_wei // 10)
        self.agent_state.reputation.simulated_stake_wei -= slash_amount
        
        # Use standardized logging
        log_reputation_change(
            agent_name=self.agent_state.name,
            worker_address=self.agent_state.wallet_address,
            task_id=task_id,
            change_type="Task Fail",
            old_score=old_score,
            new_score=self.agent_state.reputation.score,
            old_completed=old_completed,
            new_completed=self.agent_state.reputation.completed_tasks,
            old_failed=old_failed,
            new_failed=self.agent_state.reputation.failed_tasks,
            stake_change_wei=-slash_amount,
            reason="Task failed verification, reputation penalized and stake slashed"
        )

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

