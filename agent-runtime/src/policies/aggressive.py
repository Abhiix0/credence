from typing import Optional, Tuple
from .base import BasePolicy
from ..models import Agent, Task, TaskStatus


class AggressivePolicy(BasePolicy):
    """
    Aggressive bidding strategy:
    - Bids aggressively to undercut competitors (e.g. 70-80% of reward).
    - Accepts broader capability overlaps.
    - Promises faster execution duration.
    """

    def __init__(self):
        super().__init__(name="AggressivePolicy")

    def evaluate(self, agent: Agent, task: Task) -> Tuple[bool, Optional[int], Optional[int]]:
        if task.status != TaskStatus.OPEN:
            return False, None, None

        # Undercut market at 75% of maximum task reward
        proposed_price = max(int(task.reward_wei * 0.75), 1)
        # Fast turnaround: 600 seconds
        estimated_duration = 600

        return True, proposed_price, estimated_duration
