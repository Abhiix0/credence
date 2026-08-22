import logging
import os
import time
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

from ..models import Agent, Reputation, Task, TaskStatus
from ..policies import (
    BasePolicy,
    ConservativePolicy,
    AggressivePolicy,
    ReputationPolicy,
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
}


class AutonomousAgent:
    """
    Autonomous AI Agent executing on Monad testnet.
    
    Loop Lifecycle:
    Observe -> Discover -> Evaluate -> Decide -> Sign transaction -> Execute -> Submit result -> Repeat
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

    def step(self) -> None:
        """Execute a single step of the autonomous loop."""
        # 1. Observe
        self.observe()

        # 2. Discover
        tasks = self.discover()

        # 3. Evaluate & Decide & 4. Sign
        for task in tasks:
            decision = self.evaluate_and_decide(task)
            if decision:
                tx_hash = self.sign_and_submit_bid(decision)
                if tx_hash:
                    logger.info(f"Bid confirmed: tx {tx_hash}")

    def run_forever(self, interval_seconds: int = 15) -> None:
        """Continuously loop agent lifecycle."""
        logger.info("Starting Autonomous Agent loop...")
        while self.agent_state.is_active:
            try:
                self.step()
            except Exception as e:
                logger.error(f"Error in agent cycle: {e}")
            time.sleep(interval_seconds)


if __name__ == "__main__":
    agent = AutonomousAgent()
    agent.step()
