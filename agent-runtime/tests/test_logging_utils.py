"""Test logging utilities for standardized agent decision logging."""

import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logging_utils import (
    log_decision,
    log_bid_decision,
    log_worker_selection,
    log_verification_result,
    log_reputation_change,
)

# Set up logging to capture output
logging.basicConfig(level=logging.INFO)


def test_log_decision():
    """Test basic log_decision function."""
    log_decision(
        "TestAgent",
        "Test Event",
        test_field="test value",
        test_list=["item1", "item2"],
        test_dict={"key1": "value1", "key2": "value2"}
    )
    # If no exception, test passes


def test_log_bid_decision():
    """Test bid decision logging."""
    log_bid_decision(
        agent_name="WorkerBot-1",
        task_id=42,
        task_capability="code-review",
        task_reward_wei=100000000000000000,  # 0.1 ETH
        policy_name="ConservativePolicy",
        decision="BID",
        proposed_price_wei=80000000000000000,  # 0.08 ETH
        estimated_duration_sec=3600,
        reason="Policy accepted task based on capability match"
    )


def test_log_worker_selection():
    """Test worker selection logging."""
    candidates = [
        {
            "bidder": "0x1234567890123456789012345678901234567890",
            "bid_id": 1,
            "score": 87.5,
            "reputation": 92,
            "price_wei": 80000000000000000,
            "duration_sec": 3600,
        },
        {
            "bidder": "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
            "bid_id": 2,
            "score": 72.3,
            "reputation": 68,
            "price_wei": 50000000000000000,
            "duration_sec": 1800,
        }
    ]
    
    log_worker_selection(
        agent_name="BuyerBot",
        task_id=42,
        task_capability="code-review",
        task_reward_wei=100000000000000000,
        candidates=candidates,
        policy_name="ConservativePolicy",
        risk_tolerance=60.0,
        selected_worker="0x1234567890123456789012345678901234567890",
        selected_bid_id=1,
        selected_score=87.5,
        reason="Selected for strong reputation meeting conservative risk threshold"
    )


def test_log_verification_result():
    """Test verification result logging."""
    log_verification_result(
        agent_name="VerifierBot",
        task_id=42,
        worker_address="0x1234567890123456789012345678901234567890",
        verification_passed=True,
        computed_hash="8f2a7b3c4d5e6f7890abcdef01234567",
        submitted_hash="8f2a7b3c4d5e6f7890abcdef01234567",
        reason="Hash matches and URI format is valid"
    )


def test_log_reputation_change():
    """Test reputation change logging."""
    log_reputation_change(
        agent_name="WorkerBot-1",
        worker_address="0x1234567890123456789012345678901234567890",
        task_id=42,
        change_type="Task Pass",
        old_score=90,
        new_score=92,
        old_completed=15,
        new_completed=16,
        old_failed=1,
        new_failed=1,
        stake_change_wei=0,
        reason="Task completed successfully and verified"
    )


def test_log_reputation_change_with_slash():
    """Test reputation change logging with stake slash."""
    log_reputation_change(
        agent_name="BadWorkerBot",
        worker_address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
        task_id=43,
        change_type="Task Fail",
        old_score=75,
        new_score=65,
        old_completed=10,
        new_completed=10,
        old_failed=2,
        new_failed=3,
        stake_change_wei=-10000000000000000,  # -0.01 ETH slashed
        reason="Task failed verification, reputation penalized and stake slashed"
    )


if __name__ == "__main__":
    print("Testing log_decision...")
    test_log_decision()
    
    print("\nTesting log_bid_decision...")
    test_log_bid_decision()
    
    print("\nTesting log_worker_selection...")
    test_log_worker_selection()
    
    print("\nTesting log_verification_result...")
    test_log_verification_result()
    
    print("\nTesting log_reputation_change (pass)...")
    test_log_reputation_change()
    
    print("\nTesting log_reputation_change (fail with slash)...")
    test_log_reputation_change_with_slash()
    
    print("\n✅ All logging tests completed!")
