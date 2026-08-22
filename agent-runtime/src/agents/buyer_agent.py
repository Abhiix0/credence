"""
Buyer Agent for autonomous task creation and worker selection.

The BuyerAgent evaluates competing bids using policy-based scoring,
looks up worker reputations from the AgentRegistry, and selects the
best worker based on price, reputation, speed, and risk factors.
"""

import logging
import os
import time
from typing import Dict, List, Optional, Set, Tuple
from dotenv import load_dotenv

from ..models import Agent, Bid, Reputation, Task, TaskStatus
from ..policies import BasePolicy, ConservativePolicy, AggressivePolicy, ReputationPolicy, BalancedPolicy
from ..wallet import WalletSigner
from ..market import TaskMarketClient, AgentRegistryClient
from ..config import AgentConfig
from ..logging_utils import log_worker_selection, log_reputation_change

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BuyerAgent")

# Policy registry for buyer agent
BUYER_POLICY_REGISTRY: Dict[str, BasePolicy] = {
    "ConservativePolicy": ConservativePolicy(),
    "AggressivePolicy": AggressivePolicy(),
    "ReputationPolicy": ReputationPolicy(),
    "BalancedPolicy": BalancedPolicy(),
}


class BuyerAgent:
    """
    Autonomous buyer agent that evaluates bids and selects workers.
    
    Workflow:
    1. Fetch all bids for a task
    2. Look up each bidder's on-chain reputation
    3. Score bids using policy (reputation, price, speed, risk)
    4. Select highest-scoring bid above risk tolerance threshold
    5. Submit worker selection to blockchain
    """

    def __init__(
        self,
        name: Optional[str] = None,
        policy_name: Optional[str] = None,
        risk_tolerance: Optional[float] = None,
    ):
        """
        Initialize BuyerAgent.
        
        Args:
            name: Agent name (defaults to env BUYER_NAME or "BuyerAgent-01")
            policy_name: Bidding policy (defaults to env BUYER_POLICY or "ConservativePolicy")
            risk_tolerance: Minimum acceptable bid score 0-100 (defaults to env BUYER_RISK_TOLERANCE or 50.0)
        """
        # Initialize wallet signer
        self.signer = WalletSigner()
        
        # Initialize market clients
        self.market = TaskMarketClient(self.signer)
        self.registry = AgentRegistryClient(self.signer)
        
        # Initialize verifier agent (for result verification)
        try:
            self.verifier = VerifierAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize VerifierAgent: {e}")
            self.verifier = None
        
        # Initialize policy
        policy_key = policy_name or os.getenv("BUYER_POLICY", "ConservativePolicy")
        self.policy = BUYER_POLICY_REGISTRY.get(policy_key, ConservativePolicy())
        
        # Agent configuration
        self.name = name or os.getenv("BUYER_NAME", "BuyerAgent-01")
        self.wallet_address = self.signer.address
        self.risk_tolerance = risk_tolerance or float(os.getenv("BUYER_RISK_TOLERANCE", "50.0"))
        
        # Task tracking for lightweight event polling
        self._task_snapshots: Dict[int, TaskStatus] = {}  # task_id -> last_seen_status
        self._processed_tasks: Set[int] = set()  # tasks we've already handled worker selection for
        
        logger.info(f"BuyerAgent initialized: {self.name} [{self.wallet_address}]")
        logger.info(f"Active Policy: {self.policy.name}")
        logger.info(f"Risk Tolerance: {self.risk_tolerance} (minimum acceptable bid score)")

    def _build_agent_from_reputation(self, bid: Bid, reputation: Optional[Reputation]) -> Agent:
        """
        Build Agent object from bid and reputation data for policy scoring.
        
        Args:
            bid: Bid object with bidder address
            reputation: Reputation object from registry (or None for default)
            
        Returns:
            Agent object suitable for policy.score_bid()
        """
        # Use fetched reputation or create default
        if reputation:
            rep = reputation
        else:
            # Default reputation for unregistered agents
            rep = Reputation(
                agent_address=bid.bidder,
                score=50,  # Neutral score
                completed_tasks=0,
                failed_tasks=0,
                last_updated=0,
            )
        
        # Build Agent object
        # Note: capabilities are not stored in registry yet, so we use a generic list
        return Agent(
            wallet_address=bid.bidder,
            name=f"Worker-{bid.bidder[:8]}",
            balance_wei=0,  # Not needed for scoring
            capabilities=["generic"],  # Not available from registry
            reputation=rep,
            policy_name="UnknownPolicy",
            role="worker",
            is_active=True,
        )

    def evaluate_bids(self, task: Task, bids: List[Bid]) -> List[Tuple[Bid, float]]:
        """
        Evaluate all bids for a task using policy-based scoring.
        
        For each bid:
        1. Fetch bidder's on-chain reputation from AgentRegistry
        2. Build Agent object with reputation data
        3. Score bid using self.policy.score_bid()
        4. Return list of (bid, score) tuples sorted by score (highest first)
        
        Args:
            task: Task being bid on
            bids: List of bids to evaluate
            
        Returns:
            List of (Bid, score) tuples sorted by score descending
        """
        if not bids:
            logger.info(f"No bids to evaluate for Task #{task.task_id}")
            return []
        
        logger.info(f"[Evaluate] Evaluating {len(bids)} bids for Task #{task.task_id}")
        
        scored_bids = []
        
        for bid in bids:
            # Fetch bidder's on-chain reputation
            reputation = self.registry.get_agent_reputation(bid.bidder)
            
            # Build Agent object for scoring
            agent = self._build_agent_from_reputation(bid, reputation)
            
            # Score bid using policy
            score = self.policy.score_bid(agent, task, bid, bids)
            
            scored_bids.append((bid, score))
            
            # Log evaluation details
            rep_score = agent.reputation.score
            price_pct = (bid.proposed_price_wei / task.reward_wei * 100) if task.reward_wei > 0 else 0
            logger.info(
                f"  Bid #{bid.bid_id} from {bid.bidder[:10]}...: "
                f"score={score:.2f}, rep={rep_score}, price={price_pct:.1f}% of reward, "
                f"duration={bid.estimated_duration_sec}s"
            )
        
        # Sort by score descending (highest score first)
        scored_bids.sort(key=lambda x: x[1], reverse=True)
        
        return scored_bids

    def select_worker(self, task: Task, bids: List[Bid]) -> Optional[Bid]:
        """
        Select the best worker from competing bids.
        
        Selection criteria:
        1. Score bids using policy
        2. Filter out bids below risk_tolerance threshold
        3. Return highest-scoring bid, or None if all below threshold
        
        Args:
            task: Task to assign
            bids: List of competing bids
            
        Returns:
            Selected bid, or None if no acceptable bids
        """
        logger.info(f"[Select Worker] Task #{task.task_id} - Selecting from {len(bids)} bids")
        
        if not bids:
            logger.warning(f"No bids available for Task #{task.task_id}")
            return None
        
        # Evaluate and score all bids
        scored_bids = self.evaluate_bids(task, bids)
        
        if not scored_bids:
            logger.warning(f"Bid evaluation failed for Task #{task.task_id}")
            return None
        
        # Get top-scored bid
        top_bid, top_score = scored_bids[0]
        
        # Check risk tolerance threshold
        if top_score < self.risk_tolerance:
            logger.warning(
                f"Top bid score {top_score:.2f} is below risk tolerance {self.risk_tolerance}. "
                f"No worker selected for Task #{task.task_id}"
            )
            return None
        
        # Log final selection decision in PRD format
        self._log_selection_decision(task, scored_bids, top_bid, top_score)
        
        return top_bid

    def _log_selection_decision(
        self,
        task: Task,
        scored_bids: List[Tuple[Bid, float]],
        selected_bid: Bid,
        selected_score: float
    ) -> None:
        """
        Log selection decision using standardized logging utility.
        
        Args:
            task: Task being assigned
            scored_bids: All evaluated (bid, score) tuples
            selected_bid: The selected bid
            selected_score: Score of selected bid
        """
        # Build candidates list
        candidates = []
        for bid, score in scored_bids:
            reputation = self.registry.get_agent_reputation(bid.bidder)
            rep_score = reputation.score if reputation else 50
            
            candidates.append({
                "bidder": bid.bidder,
                "bid_id": bid.bid_id,
                "score": score,
                "reputation": rep_score,
                "price_wei": bid.proposed_price_wei,
                "duration_sec": bid.estimated_duration_sec,
            })
        
        # Generate reason
        reason = self._generate_selection_reason(task, selected_bid, selected_score, scored_bids)
        
        # Use standardized logging
        log_worker_selection(
            agent_name=self.name,
            task_id=task.task_id,
            task_capability=task.required_capability,
            task_reward_wei=task.reward_wei,
            candidates=candidates,
            policy_name=self.policy.name,
            risk_tolerance=self.risk_tolerance,
            selected_worker=selected_bid.bidder,
            selected_bid_id=selected_bid.bid_id,
            selected_score=selected_score,
            reason=reason
        )

    def _generate_selection_reason(
        self,
        task: Task,
        selected_bid: Bid,
        selected_score: float,
        all_scored_bids: List[Tuple[Bid, float]]
    ) -> str:
        """
        Generate one-sentence reason for selection based on score breakdown.
        
        Args:
            task: Task being assigned
            selected_bid: Selected bid
            selected_score: Score of selected bid
            all_scored_bids: All evaluated bids
            
        Returns:
            One-sentence explanation of selection
        """
        # Fetch reputation for selected bidder
        reputation = self.registry.get_agent_reputation(selected_bid.bidder)
        rep_score = reputation.score if reputation else 50
        
        price_pct = (selected_bid.proposed_price_wei / task.reward_wei * 100) if task.reward_wei > 0 else 0
        
        # Generate reason based on policy type
        policy_name = self.policy.name
        
        if policy_name == "ConservativePolicy":
            if rep_score >= 90:
                return f"Selected for exceptional reputation ({rep_score}/100) which heavily dominates conservative scoring despite {price_pct:.1f}% price point"
            elif rep_score >= 85:
                return f"Selected for strong reputation ({rep_score}/100) meeting conservative risk threshold with acceptable {price_pct:.1f}% pricing"
            else:
                return f"Selected as best available option with reputation ({rep_score}/100) and {price_pct:.1f}% price, though conservative policy prefers higher reputation"
        
        elif policy_name == "AggressivePolicy":
            if price_pct < 60:
                return f"Selected for aggressive {price_pct:.1f}% price point significantly below market, maximizing cost savings despite {rep_score}/100 reputation"
            else:
                return f"Selected for competitive {price_pct:.1f}% price with {selected_bid.estimated_duration_sec}s delivery estimate, balancing speed and cost"
        
        elif policy_name == "BalancedPolicy":
            score_margin = selected_score - all_scored_bids[1][1] if len(all_scored_bids) > 1 else selected_score
            return f"Selected for optimal balance of reputation ({rep_score}/100), price ({price_pct:.1f}%), and {selected_bid.estimated_duration_sec}s delivery, outscoring alternatives by {score_margin:.1f} points"
        
        elif policy_name == "ReputationPolicy":
            return f"Selected for superior reputation ({rep_score}/100) which dominates reputation-focused scoring at {price_pct:.1f}% price point"
        
        else:
            # Generic reason
            return f"Selected with top score ({selected_score:.2f}/100) based on reputation ({rep_score}/100), price ({price_pct:.1f}%), and delivery estimate ({selected_bid.estimated_duration_sec}s)"

    def submit_selection(self, task: Task, bid: Bid) -> Optional[str]:
        """
        Submit worker selection to blockchain.
        
        Calls TaskMarketClient.select_worker() to execute selectWorker transaction.
        
        Args:
            task: Task to assign
            bid: Selected bid
            
        Returns:
            Transaction hash if successful, None otherwise
        """
        logger.info(
            f"[Submit Selection] Task #{task.task_id} -> Worker {bid.bidder[:10]}... (Bid #{bid.bid_id})"
        )
        
        try:
            tx_hash = self.market.select_worker(task.task_id, bid.bid_id)
            
            if tx_hash:
                logger.info(f"Worker selection confirmed: tx {tx_hash}")
                return tx_hash
            else:
                logger.error(f"Failed to submit worker selection for Task #{task.task_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error submitting worker selection for Task #{task.task_id}: {e}")
            return None

    def evaluate_and_select(self, task: Task, bids: List[Bid]) -> Optional[str]:
        """
        Complete workflow: evaluate bids, select worker, submit to blockchain.
        
        Args:
            task: Task to assign
            bids: List of competing bids
            
        Returns:
            Transaction hash if successful, None otherwise
        """
        # Select best worker
        selected_bid = self.select_worker(task, bids)
        
        if not selected_bid:
            logger.warning(f"No suitable worker found for Task #{task.task_id}")
            return None
        
        # Submit selection to blockchain
        return self.submit_selection(task, selected_bid)

    def process_open_task(self, task_id: int) -> Optional[str]:
        """
        Process a single open task: fetch bids, evaluate, and select worker.
        
        Args:
            task_id: ID of the task to process
            
        Returns:
            Transaction hash if worker selected, None otherwise
        """
        logger.info(f"[Process Task] Processing Task #{task_id}")
        
        # Fetch task details
        if not self.market.contract:
            logger.error("TaskMarket contract not initialized")
            return None
        
        try:
            raw_task = self.market.contract.functions.getTask(task_id).call()
            
            task = Task(
                task_id=raw_task[0],
                creator=raw_task[1],
                specification_uri=raw_task[2],
                required_capability=raw_task[3],
                reward_wei=raw_task[4],
                deadline=raw_task[5],
                status=raw_task[6],
            )
            
            # Fetch bids for this task
            bids = self.market.fetch_bids_for_task(task_id)
            
            if not bids:
                logger.info(f"No bids yet for Task #{task_id}")
                return None
            
            # Evaluate and select worker
            return self.evaluate_and_select(task, bids)
            
        except Exception as e:
            logger.error(f"Error processing Task #{task_id}: {e}")
            return None

    def discover_my_open_tasks(self) -> List[Task]:
        """
        Discover open tasks I created (as the buyer).
        
        Returns:
            List of tasks created by me with status OPEN
        """
        if not self.market.contract:
            return []
        
        try:
            total = self.market.contract.functions.totalTasks().call()
            my_open_tasks = []
            
            my_address = self.wallet_address.lower()
            
            for task_id in range(1, total + 1):
                raw = self.market.contract.functions.getTask(task_id).call()
                
                # Status 0 = Open, check if I'm the creator
                if raw[6] == 0 and raw[1].lower() == my_address:
                    task = Task(
                        task_id=raw[0],
                        creator=raw[1],
                        specification_uri=raw[2],
                        required_capability=raw[3],
                        reward_wei=raw[4],
                        deadline=raw[5],
                        status=TaskStatus.OPEN,
                        selected_worker=None,
                    )
                    my_open_tasks.append(task)
            
            logger.info(f"[Discover My Open] Found {len(my_open_tasks)} open tasks I created")
            return my_open_tasks
            
        except Exception as e:
            logger.error(f"Error discovering my open tasks: {e}")
            return []

    def discover_my_submitted_tasks(self) -> List[Task]:
        """
        Discover tasks I created that have been submitted by workers.
        
        Returns:
            List of tasks created by me with status SUBMITTED
        """
        if not self.market.contract:
            return []
        
        try:
            total = self.market.contract.functions.totalTasks().call()
            my_submitted_tasks = []
            
            my_address = self.wallet_address.lower()
            
            for task_id in range(1, total + 1):
                raw = self.market.contract.functions.getTask(task_id).call()
                
                # Status 2 = Submitted, check if I'm the creator
                if raw[6] == 2 and raw[1].lower() == my_address:
                    task = Task(
                        task_id=raw[0],
                        creator=raw[1],
                        specification_uri=raw[2],
                        required_capability=raw[3],
                        reward_wei=raw[4],
                        deadline=raw[5],
                        status=TaskStatus.SUBMITTED,
                        selected_worker=raw[7],
                        accepted_bid_id=raw[8],
                        result_uri=raw[9],
                        result_hash=raw[10],
                    )
                    my_submitted_tasks.append(task)
            
            logger.info(f"[Discover My Submitted] Found {len(my_submitted_tasks)} submitted tasks I created")
            return my_submitted_tasks
            
        except Exception as e:
            logger.error(f"Error discovering my submitted tasks: {e}")
            return []

    def poll_task_status_changes(self) -> List[Tuple[Task, TaskStatus, TaskStatus]]:
        """
        Poll for task status changes using lightweight snapshot diff.
        
        Compares current task statuses against last-seen snapshots to detect transitions.
        
        Returns:
            List of (task, old_status, new_status) tuples for changed tasks
        """
        if not self.market.contract:
            return []
        
        try:
            total = self.market.contract.functions.totalTasks().call()
            changes = []
            
            my_address = self.wallet_address.lower()
            
            for task_id in range(1, total + 1):
                raw = self.market.contract.functions.getTask(task_id).call()
                
                # Only track tasks I created
                if raw[1].lower() != my_address:
                    continue
                
                current_status = TaskStatus(raw[6])
                old_status = self._task_snapshots.get(task_id)
                
                # Detect status change
                if old_status is not None and old_status != current_status:
                    task = Task(
                        task_id=raw[0],
                        creator=raw[1],
                        specification_uri=raw[2],
                        required_capability=raw[3],
                        reward_wei=raw[4],
                        deadline=raw[5],
                        status=current_status,
                        selected_worker=raw[7],
                        accepted_bid_id=raw[8],
                        result_uri=raw[9],
                        result_hash=raw[10],
                    )
                    changes.append((task, old_status, current_status))
                    logger.info(
                        f"[Status Change] Task #{task_id}: {old_status.value} → {current_status.value}"
                    )
                
                # Update snapshot
                self._task_snapshots[task_id] = current_status
            
            return changes
            
        except Exception as e:
            logger.error(f"Error polling task status changes: {e}")
            return []

    def run_buyer_cycle(self) -> None:
        """
        Complete buyer cycle per PRD P2.10:
        1. Discover own open tasks → fetch bids → evaluate/select worker
        2. Poll for SUBMITTED status → verify results
        3. Track status transitions → handle settlements
        """
        # Phase 1: Process open tasks (worker selection)
        open_tasks = self.discover_my_open_tasks()
        
        for task in open_tasks:
            # Skip if already processed worker selection
            if task.task_id in self._processed_tasks:
                continue
            
            # Fetch bids
            bids = self.market.fetch_bids_for_task(task.task_id)
            
            if not bids:
                logger.debug(f"No bids yet for Task #{task.task_id}")
                continue
            
            # Evaluate and select worker
            try:
                tx_hash = self.evaluate_and_select(task, bids)
                if tx_hash:
                    self._processed_tasks.add(task.task_id)
                    logger.info(f"Worker selected for Task #{task.task_id}")
            except Exception as e:
                logger.error(f"Error selecting worker for Task #{task.task_id}: {e}")
        
        # Phase 2: Process submitted tasks (verification)
        if self.verifier:
            submitted_tasks = self.discover_my_submitted_tasks()
            
            for task in submitted_tasks:
                try:
                    logger.info(f"[Verify] Verifying submitted Task #{task.task_id}")
                    self.verifier.verify_and_submit(task, use_light_verification=False)
                except Exception as e:
                    logger.error(f"Error verifying Task #{task.task_id}: {e}")
        
        # Phase 3: Poll for status changes (handle settlements)
        status_changes = self.poll_task_status_changes()
        
        for task, old_status, new_status in status_changes:
            # Handle settlement events
            if new_status in [TaskStatus.VERIFIED_PASS, TaskStatus.VERIFIED_FAIL]:
                self._handle_task_settlement(task, new_status)

    def _handle_task_settlement(self, task: Task, status: TaskStatus) -> None:
        """
        Handle task settlement: update reputation tracking.
        
        Since there's no on-chain stake contract yet, this simulates stake slashing
        by tracking it locally in reputation.simulated_stake_wei.
        
        Args:
            task: Settled task
            status: VERIFIED_PASS or VERIFIED_FAIL
        """
        passed = (status == TaskStatus.VERIFIED_PASS)
        
        # Fetch current reputation
        if task.selected_worker:
            reputation = self.registry.get_agent_reputation(task.selected_worker)
            
            if reputation:
                # Calculate simulated changes
                old_score = reputation.score
                old_completed = reputation.completed_tasks
                old_failed = reputation.failed_tasks
                old_stake = reputation.simulated_stake_wei
                
                if passed:
                    new_score = min(100, old_score + 2)
                    new_completed = old_completed + 1
                    new_failed = old_failed
                    stake_change = 0
                    change_type = "Task Pass"
                else:
                    new_score = max(0, old_score - 10)
                    new_completed = old_completed
                    new_failed = old_failed + 1
                    stake_change = -min(old_stake, task.reward_wei // 10)
                    change_type = "Task Fail"
                
                # Use standardized logging
                log_reputation_change(
                    agent_name=self.name,
                    worker_address=task.selected_worker,
                    task_id=task.task_id,
                    change_type=change_type,
                    old_score=old_score,
                    new_score=new_score,
                    old_completed=old_completed,
                    new_completed=new_completed,
                    old_failed=old_failed,
                    new_failed=new_failed,
                    stake_change_wei=stake_change,
                    reason=f"Task settlement: {'worker delivered valid result' if passed else 'worker failed verification'}"
                )

    def step(self) -> None:
        """
        Execute one cycle of the buyer agent.
        
        Complete buyer workflow:
        1. Discover open tasks I created → select workers
        2. Discover submitted tasks → verify results
        3. Poll status changes → handle settlements
        """
        try:
            self.run_buyer_cycle()
        except Exception as e:
            logger.error(f"Error in buyer cycle: {e}")

    def run_forever(self, interval_seconds: int = 15) -> None:
        """Continuously loop buyer agent lifecycle."""
        logger.info("Starting BuyerAgent loop...")
        logger.info("Agent will: select workers, verify results, handle settlements")
        while True:
            try:
                self.step()
            except Exception as e:
                logger.error(f"Error in agent loop: {e}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    """
    Standalone buyer agent execution.
    
    Environment variables required:
    - BUYER_PRIVATE_KEY or AGENT_PRIVATE_KEY: Private key
    - BUYER_POLICY: Selection policy (ConservativePolicy/AggressivePolicy/BalancedPolicy)
    - BUYER_RISK_TOLERANCE: Minimum acceptable bid score (0-100)
    - TASK_MARKET_CONTRACT_ADDRESS: TaskMarket contract address
    - AGENT_REGISTRY_CONTRACT_ADDRESS: AgentRegistry contract address
    - MONAD_RPC_URL: Monad testnet RPC URL
    """
    buyer = BuyerAgent()
    logger.info("BuyerAgent ready. Use buyer.process_open_task(task_id) to process tasks.")
