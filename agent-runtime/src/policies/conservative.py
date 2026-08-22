from typing import Optional, Tuple
from .base import BasePolicy
from ..models import Agent, Task, TaskStatus


class ConservativePolicy(BasePolicy):
    """
    Conservative bidding strategy:
    - Only bids if the agent strictly matches the required capability.
    - Demands 90-95% of the total posted reward.
    - Requests generous execution duration buffer.
    """

    def __init__(self):
        super().__init__(name="ConservativePolicy")

    def evaluate(self, agent: Agent, task: Task) -> Tuple[bool, Optional[int], Optional[int]]:
        if task.status != TaskStatus.OPEN:
            return False, None, None

        # Check strict capability match
        if task.required_capability not in agent.capabilities:
            return False, None, None

        # Bid 95% of task reward to ensure profitability
        proposed_price = int(task.reward_wei * 0.95)
        # Safe 1800 second turnaround estimation
        estimated_duration = 1800

        return True, proposed_price, estimated_duration
