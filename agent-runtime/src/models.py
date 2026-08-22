from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    OPEN = "Open"
    ASSIGNED = "Assigned"
    SUBMITTED = "Submitted"
    VERIFIED_PASS = "VerifiedPass"
    VERIFIED_FAIL = "VerifiedFail"
    CANCELLED = "Cancelled"


class Reputation(BaseModel):
    """Reputation record of an autonomous agent."""
    agent_address: str
    score: int = 100
    completed_tasks: int = 0
    failed_tasks: int = 0
    last_updated: int = 0


class Agent(BaseModel):
    """Autonomous agent entity."""
    wallet_address: str
    name: str = "AutonomousAgent"
    balance_wei: int = 0
    capabilities: List[str] = Field(default_factory=list)
    reputation: Reputation
    policy_name: str = "ConservativePolicy"
    is_active: bool = True


class Task(BaseModel):
    """Task specification posted to TaskMarket."""
    task_id: int
    creator: str
    specification_uri: str
    required_capability: str
    reward_wei: int
    deadline: int
    status: TaskStatus = TaskStatus.OPEN
    selected_worker: Optional[str] = None
    accepted_bid_id: Optional[int] = None
    result_uri: Optional[str] = None
    result_hash: Optional[str] = None


class Bid(BaseModel):
    """Offer submitted by an agent for a task."""
    bid_id: int
    task_id: int
    bidder: str
    proposed_price_wei: int
    estimated_duration_sec: int
    timestamp: int
    is_accepted: bool = False


class Settlement(BaseModel):
    """Settlement outcome for a task lifecycle."""
    settlement_id: str
    task_id: int
    recipient: str
    amount_wei: int
    timestamp: int
    result_proof: str
    passed: bool
