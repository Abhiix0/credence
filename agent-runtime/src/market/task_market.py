import os
from typing import List, Optional
from web3 import Web3
from ..models import Task, TaskStatus, Bid
from ..wallet.signer import WalletSigner

# Minimal ABI for TaskMarket contract interactions
TASK_MARKET_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "taskId", "type": "uint256"}],
        "name": "getTask",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "address", "name": "creator", "type": "address"},
                    {"internalType": "string", "name": "specificationUri", "type": "string"},
                    {"internalType": "string", "name": "requiredCapability", "type": "string"},
                    {"internalType": "uint256", "name": "reward", "type": "uint256"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                    {"internalType": "uint8", "name": "status", "type": "uint8"},
                    {"internalType": "address", "name": "selectedWorker", "type": "address"},
                    {"internalType": "uint256", "name": "acceptedBidId", "type": "uint256"},
                    {"internalType": "string", "name": "resultUri", "type": "string"},
                    {"internalType": "bytes32", "name": "resultHash", "type": "bytes32"},
                ],
                "internalType": "struct ITaskMarket.Task",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "totalTasks",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "taskId", "type": "uint256"},
            {"internalType": "uint256", "name": "proposedPrice", "type": "uint256"},
            {"internalType": "uint256", "name": "estimatedDuration", "type": "uint256"},
        ],
        "name": "submitBid",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "taskId", "type": "uint256"},
            {"internalType": "string", "name": "resultUri", "type": "string"},
            {"internalType": "bytes32", "name": "resultHash", "type": "bytes32"},
        ],
        "name": "submitResult",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "bidId", "type": "uint256"}],
        "name": "getBid",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "uint256", "name": "taskId", "type": "uint256"},
                    {"internalType": "address", "name": "bidder", "type": "address"},
                    {"internalType": "uint256", "name": "proposedPrice", "type": "uint256"},
                    {"internalType": "uint256", "name": "estimatedDuration", "type": "uint256"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "bool", "name": "isAccepted", "type": "bool"},
                ],
                "internalType": "struct ITaskMarket.Bid",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "taskId", "type": "uint256"}],
        "name": "getTaskBids",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "taskId", "type": "uint256"},
            {"internalType": "uint256", "name": "bidId", "type": "uint256"},
        ],
        "name": "selectWorker",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "taskId", "type": "uint256"},
            {"internalType": "bool", "name": "passed", "type": "bool"},
        ],
        "name": "verifyResult",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


class TaskMarketClient:
    """Client for discovering tasks and executing market operations on Monad."""

    def __init__(self, signer: WalletSigner, contract_address: Optional[str] = None):
        self.signer = signer
        self.w3 = signer.w3
        self.contract_address = contract_address or os.getenv("TASK_MARKET_CONTRACT_ADDRESS")
        
        if self.contract_address and self.w3.is_address(self.contract_address):
            self.contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contract_address),
                abi=TASK_MARKET_ABI
            )
        else:
            self.contract = None

    def fetch_open_tasks(self) -> List[Task]:
        """Fetch open tasks from the contract."""
        if not self.contract:
            return []
        
        try:
            total = self.contract.functions.totalTasks().call()
            open_tasks = []
            for t_id in range(1, total + 1):
                raw = self.contract.functions.getTask(t_id).call()
                # Status 0 = Open
                if raw[6] == 0:
                    open_tasks.append(
                        Task(
                            task_id=raw[0],
                            creator=raw[1],
                            specification_uri=raw[2],
                            required_capability=raw[3],
                            reward_wei=raw[4],
                            deadline=raw[5],
                            status=TaskStatus.OPEN,
                            selected_worker=raw[7] if raw[7] != "0x0000000000000000000000000000000000000000" else None,
                        )
                    )
            return open_tasks
        except Exception:
            return []

    def submit_bid(self, task_id: int, proposed_price: int, estimated_duration: int) -> Optional[str]:
        """Submit bid to TaskMarket contract."""
        if not self.contract or not self.signer.account:
            return None

        tx = self.contract.functions.submitBid(
            task_id, proposed_price, estimated_duration
        ).build_transaction({
            "from": self.signer.address,
            "gas": 300000,
        })
        return self.signer.sign_and_send_transaction(tx)

    def submit_task_result(self, task_id: int, result_uri: str, result_hash: bytes) -> Optional[str]:
        """Submit completed work proof to TaskMarket contract."""
        if not self.contract or not self.signer.account:
            return None

        tx = self.contract.functions.submitResult(
            task_id, result_uri, result_hash
        ).build_transaction({
            "from": self.signer.address,
            "gas": 300000,
        })
        return self.signer.sign_and_send_transaction(tx)

    def fetch_bid(self, bid_id: int) -> Optional[Bid]:
        """Fetch a single bid by ID from the contract."""
        if not self.contract:
            return None
        
        try:
            raw = self.contract.functions.getBid(bid_id).call()
            return Bid(
                bid_id=raw[0],
                task_id=raw[1],
                bidder=raw[2],
                proposed_price_wei=raw[3],
                estimated_duration_sec=raw[4],
                timestamp=raw[5],
                is_accepted=raw[6],
            )
        except Exception:
            return None

    def fetch_bids_for_task(self, task_id: int) -> List[Bid]:
        """Fetch all bids for a specific task."""
        if not self.contract:
            return []
        
        try:
            bid_ids = self.contract.functions.getTaskBids(task_id).call()
            bids = []
            for bid_id in bid_ids:
                bid = self.fetch_bid(bid_id)
                if bid:
                    bids.append(bid)
            return bids
        except Exception:
            return []

    def select_worker(self, task_id: int, bid_id: int) -> Optional[str]:
        """Select a worker for a task by accepting their bid."""
        if not self.contract or not self.signer.account:
            return None

        tx = self.contract.functions.selectWorker(
            task_id, bid_id
        ).build_transaction({
            "from": self.signer.address,
            "gas": 300000,
        })
        return self.signer.sign_and_send_transaction(tx)

    def verify_result(self, task_id: int, passed: bool) -> Optional[str]:
        """Verify task result and settle payment."""
        if not self.contract or not self.signer.account:
            return None

        tx = self.contract.functions.verifyResult(
            task_id, passed
        ).build_transaction({
            "from": self.signer.address,
            "gas": 400000,  # Higher gas for settlement logic
        })
        return self.signer.sign_and_send_transaction(tx)
