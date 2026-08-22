"""Configuration management for autonomous agents."""
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AgentConfig:
    """Configuration for a single autonomous agent."""
    name: str
    private_key: str
    policy_name: str
    capabilities: List[str]
    role: str  # "buyer" | "worker" | "verifier"
    risk_tolerance: float = 0.5
    max_bid_wei: Optional[int] = None
    min_balance_wei: int = 0


def load_agent_configs_from_env(prefix: str = "AGENT") -> List[AgentConfig]:
    """
    Load agent configurations from numbered environment variables.
    
    Expected format:
        AGENT_1_NAME=WorkerBot1
        AGENT_1_PRIVATE_KEY=0x...
        AGENT_1_POLICY=ConservativePolicy
        AGENT_1_CAPABILITIES=coding,testing
        AGENT_1_ROLE=worker
        AGENT_1_RISK_TOLERANCE=0.3 (optional)
        AGENT_1_MAX_BID_WEI=1000000000000000000 (optional)
        AGENT_1_MIN_BALANCE_WEI=100000000000000000 (optional)
    
    Args:
        prefix: Environment variable prefix (default: "AGENT")
    
    Returns:
        List of AgentConfig objects
    """
    configs = []
    index = 1
    
    while True:
        name_key = f"{prefix}_{index}_NAME"
        if name_key not in os.environ:
            break
        
        # Required fields
        name = os.environ[name_key]
        private_key = os.environ.get(f"{prefix}_{index}_PRIVATE_KEY", "")
        policy_name = os.environ.get(f"{prefix}_{index}_POLICY", "ConservativePolicy")
        
        # Parse capabilities (comma-separated)
        capabilities_str = os.environ.get(f"{prefix}_{index}_CAPABILITIES", "")
        capabilities = [cap.strip() for cap in capabilities_str.split(",") if cap.strip()]
        
        role = os.environ.get(f"{prefix}_{index}_ROLE", "worker")
        
        # Optional fields
        risk_tolerance = float(os.environ.get(f"{prefix}_{index}_RISK_TOLERANCE", "0.5"))
        
        max_bid_wei_str = os.environ.get(f"{prefix}_{index}_MAX_BID_WEI")
        max_bid_wei = int(max_bid_wei_str) if max_bid_wei_str else None
        
        min_balance_wei = int(os.environ.get(f"{prefix}_{index}_MIN_BALANCE_WEI", "0"))
        
        config = AgentConfig(
            name=name,
            private_key=private_key,
            policy_name=policy_name,
            capabilities=capabilities,
            role=role,
            risk_tolerance=risk_tolerance,
            max_bid_wei=max_bid_wei,
            min_balance_wei=min_balance_wei
        )
        
        configs.append(config)
        index += 1
    
    return configs
