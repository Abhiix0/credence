"""
Verifier Agent for autonomous task result verification.

IMPORTANT AUTHORIZATION CONSTRAINT:
The contract's verifyResult() function requires msg.sender to be either:
1. The task creator (buyer who posted the task), OR
2. The contract owner (deployer)

This means the verifier agent MUST run with one of these private keys:
- VERIFIER_MODE="buyer": Use the buyer's private key (who created the task)
- VERIFIER_MODE="owner": Use the contract deployer/owner's private key

If you run with a worker's key or any other unauthorized key, verification
transactions will fail with "Unauthorized verifier" error.

For hackathon/demo purposes:
- Use VERIFIER_MODE="owner" and set VERIFIER_PRIVATE_KEY to the deployer key
- Or create a separate buyer agent that also acts as verifier for its own tasks
"""

import logging
import os
from typing import Optional
from dotenv import load_dotenv

from ..models import Task, TaskStatus
from ..wallet import WalletSigner
from ..market import TaskMarketClient
from ..execution import TaskExecutor

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("VerifierAgent")


class VerifierAgent:
    """
    Autonomous verifier agent that validates task results and submits verification.
    
    Architecture:
    - Re-executes tasks deterministically to verify worker's submitted results
    - Compares computed hash against task.result_hash
    - Submits verification (pass/fail) to the TaskMarket contract
    
    Authorization Requirements:
    - Must run with task creator's key OR contract owner's key
    - See module docstring for detailed explanation
    """

    def __init__(
        self,
        name: Optional[str] = None,
        verifier_mode: Optional[str] = None,
    ):
        """
        Initialize VerifierAgent.
        
        Args:
            name: Agent name (defaults to env VERIFIER_NAME or "VerifierAgent-01")
            verifier_mode: Authorization mode - "owner" or "buyer" (defaults to env VERIFIER_MODE)
        """
        # Initialize wallet signer
        # Verifier must use appropriate private key (owner or buyer)
        private_key = os.getenv("VERIFIER_PRIVATE_KEY") or os.getenv("AGENT_PRIVATE_KEY")
        if not private_key:
            raise ValueError(
                "VERIFIER_PRIVATE_KEY must be set. "
                "Use contract owner key (VERIFIER_MODE=owner) or buyer key (VERIFIER_MODE=buyer)"
            )
        
        self.signer = WalletSigner(private_key=private_key)
        self.market = TaskMarketClient(self.signer)
        self.executor = TaskExecutor()
        
        self.name = name or os.getenv("VERIFIER_NAME", "VerifierAgent-01")
        self.verifier_mode = verifier_mode or os.getenv("VERIFIER_MODE", "owner")
        
        if self.verifier_mode not in ["owner", "buyer"]:
            logger.warning(
                f"Invalid VERIFIER_MODE '{self.verifier_mode}'. "
                "Must be 'owner' or 'buyer'. Defaulting to 'owner'."
            )
            self.verifier_mode = "owner"
        
        logger.info(f"VerifierAgent initialized: {self.name} [{self.signer.address}]")
        logger.info(f"Verification mode: {self.verifier_mode}")
        logger.info(
            "⚠️  AUTHORIZATION: This agent must run with task.creator or contract owner key"
        )

    def verify(self, task: Task) -> bool:
        """
        Verify task result by re-executing and comparing hashes.
        
        For hackathon MVP, this performs deterministic verification:
        1. Re-run TaskExecutor.execute() on the same task
        2. Compare computed result_hash against task.result_hash
        3. Optionally validate result_uri format
        
        Args:
            task: Task object with result_hash and result_uri to verify
            
        Returns:
            True if verification passes, False otherwise
        """
        logger.info(f"[Verify] Starting verification for Task #{task.task_id}")
        
        # Basic validation checks
        if task.status != TaskStatus.SUBMITTED:
            logger.warning(f"Task #{task.task_id} status is {task.status}, expected SUBMITTED")
            return False
        
        if not task.result_hash or task.result_hash == b'\x00' * 32:
            logger.warning(f"Task #{task.task_id} has invalid result_hash")
            return False
        
        if not task.result_uri:
            logger.warning(f"Task #{task.task_id} has empty result_uri")
            return False
        
        try:
            # Re-execute task to compute expected result
            logger.info(f"Re-executing task {task.task_id} with capability: {task.required_capability}")
            computed_uri, computed_hash = self.executor.execute(task)
            
            # Compare computed hash with submitted hash
            hash_match = computed_hash == task.result_hash
            
            logger.info(f"Hash comparison for Task #{task.task_id}:")
            logger.info(f"  Submitted:  {task.result_hash.hex()}")
            logger.info(f"  Computed:   {computed_hash.hex()}")
            logger.info(f"  Match:      {hash_match}")
            
            # Validate URI format (should match expected pattern)
            uri_valid = task.result_uri.startswith(f"ipfs://result-{task.task_id}-")
            
            if not uri_valid:
                logger.warning(f"Task #{task.task_id} has invalid result_uri format: {task.result_uri}")
            
            # Verification passes if hash matches and URI format is valid
            verification_passed = hash_match and uri_valid
            
            logger.info(f"[Verify] Task #{task.task_id} verification: {'PASS' if verification_passed else 'FAIL'}")
            return verification_passed
            
        except Exception as e:
            logger.error(f"[Verify] Error verifying Task #{task.task_id}: {e}")
            return False

    def verify_capability_specific(self, task: Task) -> bool:
        """
        Lighter verification that checks capability-specific result format.
        
        Alternative to full re-execution, checks if the result format is valid
        for the task's required capability without re-running AI inference.
        
        Args:
            task: Task to verify
            
        Returns:
            True if result format is valid, False otherwise
        """
        logger.info(f"[Verify-Light] Checking result format for Task #{task.task_id}")
        
        capability = task.required_capability.lower().strip()
        
        # Basic checks
        if not task.result_hash or not task.result_uri:
            return False
        
        # Verify URI format
        uri_pattern = f"ipfs://result-{task.task_id}-"
        if not task.result_uri.startswith(uri_pattern):
            logger.warning(f"Invalid URI format for Task #{task.task_id}")
            return False
        
        # Extract hash prefix from URI and verify consistency
        # URI format: ipfs://result-{task_id}-{hash[:12]}
        try:
            uri_hash_prefix = task.result_uri.split("-")[-1]
            actual_hash_prefix = task.result_hash.hex()[:12]
            
            if uri_hash_prefix != actual_hash_prefix:
                logger.warning(
                    f"Hash prefix mismatch in URI for Task #{task.task_id}: "
                    f"URI={uri_hash_prefix}, Hash={actual_hash_prefix}"
                )
                return False
        except Exception as e:
            logger.warning(f"Failed to parse URI hash prefix: {e}")
            return False
        
        # Capability-specific validation could be added here
        # For now, format validation is sufficient for hackathon
        
        logger.info(f"[Verify-Light] Task #{task.task_id} format validation: PASS")
        return True

    def submit_verification(self, task_id: int, passed: bool) -> Optional[str]:
        """
        Submit verification result to TaskMarket contract.
        
        IMPORTANT: This transaction will FAIL if the verifier's wallet is not
        authorized (must be task.creator or contract owner).
        
        Args:
            task_id: ID of the task to verify
            passed: True if verification passed, False if failed
            
        Returns:
            Transaction hash if successful, None if failed
        """
        logger.info(
            f"[Submit Verification] Task #{task_id} -> "
            f"{'PASS ✅' if passed else 'FAIL ❌'}"
        )
        
        try:
            tx_hash = self.market.verify_result(task_id, passed)
            
            if tx_hash:
                logger.info(f"Verification submitted: tx {tx_hash}")
                return tx_hash
            else:
                logger.error(f"Failed to submit verification for Task #{task_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error submitting verification for Task #{task_id}: {e}")
            return None

    def verify_and_submit(self, task: Task, use_light_verification: bool = False) -> Optional[str]:
        """
        Verify task result and submit verification to blockchain.
        
        Complete workflow:
        1. Verify the task result (full or light verification)
        2. Submit verification result to contract
        
        Args:
            task: Task to verify
            use_light_verification: If True, use lighter format-only verification
            
        Returns:
            Transaction hash if successful, None if failed
        """
        # Perform verification
        if use_light_verification:
            passed = self.verify_capability_specific(task)
        else:
            passed = self.verify(task)
        
        # Submit verification result
        return self.submit_verification(task.task_id, passed)

    def discover_submitted_tasks(self) -> list[Task]:
        """
        Discover tasks in 'Submitted' status that need verification.
        
        Returns:
            List of tasks awaiting verification
        """
        if not self.market.contract:
            return []
        
        try:
            total = self.market.contract.functions.totalTasks().call()
            submitted_tasks = []
            
            for task_id in range(1, total + 1):
                raw = self.market.contract.functions.getTask(task_id).call()
                
                # Status 2 = Submitted
                if raw[6] == 2:
                    task = Task(
                        task_id=raw[0],
                        creator=raw[1],
                        specification_uri=raw[2],
                        required_capability=raw[3],
                        reward_wei=raw[4],
                        deadline=raw[5],
                        status=TaskStatus.SUBMITTED,
                        selected_worker=raw[7] if raw[7] != "0x0000000000000000000000000000000000000000" else None,
                        accepted_bid_id=raw[8] if raw[8] > 0 else None,
                        result_uri=raw[9],
                        result_hash=raw[10],
                    )
                    submitted_tasks.append(task)
            
            logger.info(f"[Discover] Found {len(submitted_tasks)} tasks awaiting verification")
            return submitted_tasks
            
        except Exception as e:
            logger.error(f"Error discovering submitted tasks: {e}")
            return []

    def verify_all_pending(self, use_light_verification: bool = False) -> None:
        """
        Discover and verify all pending tasks.
        
        Complete autonomous loop:
        1. Discover all tasks in 'Submitted' status
        2. Verify each task
        3. Submit verification results to blockchain
        
        Args:
            use_light_verification: If True, use lighter verification method
        """
        logger.info("[Verify All] Starting verification cycle...")
        
        tasks = self.discover_submitted_tasks()
        
        if not tasks:
            logger.info("No tasks pending verification")
            return
        
        for task in tasks:
            try:
                self.verify_and_submit(task, use_light_verification=use_light_verification)
            except Exception as e:
                logger.error(f"Failed to verify Task #{task.task_id}: {e}")


if __name__ == "__main__":
    """
    Standalone verifier agent execution.
    
    Environment variables required:
    - VERIFIER_PRIVATE_KEY: Private key (must be task creator or contract owner)
    - VERIFIER_MODE: "owner" or "buyer"
    - TASK_MARKET_CONTRACT_ADDRESS: TaskMarket contract address
    - MONAD_RPC_URL: Monad testnet RPC URL
    """
    verifier = VerifierAgent()
    verifier.verify_all_pending()
