import pytest
from src.models import Agent, Reputation, Task, TaskStatus
from src.policies import ConservativePolicy, AggressivePolicy, ReputationPolicy
from src.execution.executor import TaskExecutor


def test_conservative_policy():
    policy = ConservativePolicy()
    agent = Agent(
        wallet_address="0x1111111111111111111111111111111111111111",
        capabilities=["data-analysis"],
        reputation=Reputation(agent_address="0x1111111111111111111111111111111111111111"),
    )

    # Matching capability
    task = Task(
        task_id=1,
        creator="0x9999999999999999999999999999999999999999",
        specification_uri="ipfs://spec-1",
        required_capability="data-analysis",
        reward_wei=1000000,
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    should_bid, price, duration = policy.evaluate(agent, task)
    assert should_bid is True
    assert price == 950000
    assert duration == 1800

    # Unmatched capability
    task_unmatched = task.model_copy(update={"required_capability": "unsupported-skill"})
    should_bid, price, duration = policy.evaluate(agent, task_unmatched)
    assert should_bid is False


def test_aggressive_policy():
    policy = AggressivePolicy()
    agent = Agent(
        wallet_address="0x2222222222222222222222222222222222222222",
        capabilities=["code-audit"],
        reputation=Reputation(agent_address="0x2222222222222222222222222222222222222222"),
    )
    task = Task(
        task_id=2,
        creator="0x9999999999999999999999999999999999999999",
        specification_uri="ipfs://spec-2",
        required_capability="code-audit",
        reward_wei=1000000,
        deadline=9999999999,
        status=TaskStatus.OPEN,
    )
    should_bid, price, duration = policy.evaluate(agent, task)
    assert should_bid is True
    assert price == 750000
    assert duration == 600


def test_task_executor():
    executor = TaskExecutor()
    task = Task(
        task_id=10,
        creator="0x9999999999999999999999999999999999999999",
        specification_uri="ipfs://test-spec",
        required_capability="text-processing",
        reward_wei=500000,
        deadline=9999999999,
    )
    uri, raw_hash = executor.execute(task)
    assert uri.startswith("ipfs://result-10-")
    assert len(raw_hash) == 32
