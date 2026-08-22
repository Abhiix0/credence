import os
from typing import Optional
from web3 import Web3
from ..models import Reputation
from ..wallet.signer import WalletSigner

# Minimal ABI for AgentRegistry contract interactions
AGENT_REGISTRY_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
        "name": "getAgent",
        "outputs": [
            {
                "components": [
                    {"internalType": "address", "name": "wallet", "type": "address"},
                    {"internalType": "string", "name": "name", "type": "string"},
                    {"internalType": "string[]", "name": "capabilities", "type": "string[]"},
                    {"internalType": "uint256", "name": "reputationScore", "type": "uint256"},
                    {"internalType": "uint256", "name": "completedTasks", "type": "uint256"},
                    {"internalType": "uint256", "name": "failedTasks", "type": "uint256"},
                    {"internalType": "bool", "name": "isRegistered", "type": "bool"},
                ],
                "internalType": "struct IAgentRegistry.Agent",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "agent", "type": "address"}],
        "name": "isRegisteredAgent",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string[]", "name": "capabilities", "type": "string[]"},
        ],
        "name": "registerAgent",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


class AgentRegistryClient:
    """Client for interacting with AgentRegistry contract."""

    def __init__(self, signer: WalletSigner, contract_address: Optional[str] = None):
        self.signer = signer
        self.w3 = signer.w3
        self.contract_address = contract_address or os.getenv("AGENT_REGISTRY_CONTRACT_ADDRESS")
        
        if self.contract_address and self.w3.is_address(self.contract_address):
            self.contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contract_address),
                abi=AGENT_REGISTRY_ABI
            )
        else:
            self.contract = None

    def get_agent_reputation(self, agent_address: str) -> Optional[Reputation]:
        """
        Fetch agent's on-chain reputation from AgentRegistry.
        
        Args:
            agent_address: Wallet address of the agent
            
        Returns:
            Reputation object with score and task history, or None if not found
        """
        if not self.contract:
            return None
        
        try:
            # Ensure address is checksummed
            checksum_addr = self.w3.to_checksum_address(agent_address)
            raw = self.contract.functions.getAgent(checksum_addr).call()
            
            # Check if agent is registered
            if not raw[6]:  # isRegistered
                return None
            
            # Map to Reputation model
            return Reputation(
                agent_address=raw[0],  # wallet
                score=raw[3],  # reputationScore
                completed_tasks=raw[4],  # completedTasks
                failed_tasks=raw[5],  # failedTasks
                last_updated=0,  # Contract doesn't track this
            )
        except Exception:
            return None

    def is_registered(self, agent_address: str) -> bool:
        """
        Check if an agent is registered in the registry.
        
        Args:
            agent_address: Wallet address to check
            
        Returns:
            True if registered, False otherwise
        """
        if not self.contract:
            return False
        
        try:
            checksum_addr = self.w3.to_checksum_address(agent_address)
            return self.contract.functions.isRegisteredAgent(checksum_addr).call()
        except Exception:
            return False

    def register_agent(self, name: str, capabilities: list[str]) -> Optional[str]:
        """
        Register agent in the registry.
        
        Args:
            name: Agent name
            capabilities: List of capability strings
            
        Returns:
            Transaction hash if successful, None otherwise
        """
        if not self.contract or not self.signer.account:
            return None

        tx = self.contract.functions.registerAgent(
            name, capabilities
        ).build_transaction({
            "from": self.signer.address,
            "gas": 300000,
        })
        return self.signer.sign_and_send_transaction(tx)
