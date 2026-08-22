"""
Buyer Agent for autonomous task creation and worker selection.

The BuyerAgent evaluates competing bids using policy-based scoring,
looks up worker reputations from the AgentRegistry, and selects the
best worker based on price, reputation, speed, and risk factors.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

from ..models import Agent, Bid, Reputation, Task
from ..policies import BasePolicy, ConservativePolicy, AggressivePolicy, ReputationPolicy, BalancedPolicy
from ..wallet import WalletSigner
from ..market import TaskMarketClient, AgentRegistryClient
from ..config import AgentConfig

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
        
        # Initialize policy
        policy_key = policy_name or os.getenv("BUYER_POLICY", "ConservativePolicy")
        self.policy = BUYER_POLICY_REGISTRY.get(policy_key, ConservativePolicy())
        
        # Agent configuration
        self.name = name or os.getenv("BUYER_NAME", "BuyerAgent-01")
        self.wallet_address = self.signer.address
        self.risk_tolerance = risk_tolerance or float(os.getenv("BUYER_RISK_TOLERANCE", "50.0"))
        
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
        Log selection decision in PRD-specified format.
        
        Format per PRD P2.12:
        - Agent name and task ID
        - All candidates with price/reputation
        - Active policy name
        - Final decision (selected worker)
        - One-sentence reason derived from score breakdown
        
        Args:
            task: Task being assigned
            scored_bids: All evaluated (bid, score) tuples
            selected_bid: The selected bid
            selected_score: Score of selected bid
        """
        logger.info("="*70)
        logger.info(f"WORKER SELECTION DECISION - {self.name}")
        logger.info("="*70)
        logger.info(f"Task ID: #{task.task_id}")
        logger.info(f"Required Capability: {task.required_capability}")
        logger.info(f"Task Reward: {task.reward_wei} wei ({task.reward_wei / 1e18:.6f} ETH)")
        logger.info("-"*70)
        
        # Log all candidates
        logger.info(f"Evaluated Candidates ({len(scored_bids)} bids):")
        for i, (bid, score) in enumerate(scored_bids, 1):
            reputation = self.registry.get_agent_reputation(bid.bidder)
            rep_score = reputation.score if reputation else 50
            price_eth = bid.proposed_price_wei / 1e18
            price_pct = (bid.proposed_price_wei / task.reward_wei * 100) if task.reward_wei > 0 else 0
            
            marker = "👑 SELECTED" if bid.bid_id == selected_bid.bid_id else f"   #{i}"
            logger.info(
                f"  {marker} | Bid #{bid.bid_id} | Worker: {bid.bidder[:10]}... | "
                f"Score: {score:.2f} | Rep: {rep_score} | "
                f"Price: {price_eth:.6f} ETH ({price_pct:.1f}%) | "
                f"Duration: {bid.estimated_duration_sec}s"
            )
        
        logger.info("-"*70)
        logger.info(f"Active Policy: {self.policy.name}")
        logger.info(f"Risk Tolerance Threshold: {self.risk_tolerance}")
        
        # Generate reason based on policy type and score breakdown
        reason = self._generate_selection_reason(task, selected_bid, selected_score, scored_bids)
        
        logger.info("-"*70)
        logger.info(f"FINAL DECISION: Selected Worker {selected_bid.bidder[:10]}... (Bid #{selected_bid.bid_id})")
        logger.info(f"Selection Score: {selected_score:.2f}/100")
        logger.info(f"Reason: {reason}")
        logger.info("="*70)

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
