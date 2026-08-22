"""
Standardized logging utilities for agent decision events.

Provides consistent block-format logging for:
- Worker selection decisions (buyer)
- Bid decisions (worker)
- Verification results (verifier)
- Reputation changes

Format follows PRD specification with clear block structure.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("AgentDecisions")


def log_decision(
    agent_name: str,
    event: str,
    **fields
) -> None:
    """
    Log agent decision in standardized block format.
    
    Format:
        ========================================
        [Agent Name]
        Event: <event type>
        ========================================
        Field1: value1
        Field2: value2
        ...
        ========================================
    
    Args:
        agent_name: Name of the agent making the decision
        event: Type of event (e.g., "Worker Selection", "Bid Decision", "Verification")
        **fields: Additional key-value pairs to log in the block
    
    Example:
        log_decision(
            "BuyerAgent-01",
            "Worker Selection",
            task_id=42,
            found_task="Task #42",
            candidates=["Worker A (score: 85)", "Worker B (score: 72)"],
            policy="ConservativePolicy",
            decision="Selected Worker A",
            reason="Highest reputation score with acceptable price"
        )
    """
    # Build the log block
    separator = "=" * 70
    
    lines = [
        separator,
        f"[{agent_name}]",
        f"Event: {event}",
        separator,
    ]
    
    # Add all fields in order provided
    for key, value in fields.items():
        # Format field name (convert snake_case to Title Case)
        field_name = key.replace('_', ' ').title()
        
        # Format value based on type
        if isinstance(value, list):
            # Multi-line list formatting
            lines.append(f"{field_name}:")
            for item in value:
                lines.append(f"  • {item}")
        elif isinstance(value, dict):
            # Dictionary formatting
            lines.append(f"{field_name}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            # Single line formatting
            lines.append(f"{field_name}: {value}")
    
    lines.append(separator)
    
    # Log the complete block
    log_message = "\n".join(lines)
    logger.info(log_message)


def log_bid_decision(
    agent_name: str,
    task_id: int,
    task_capability: str,
    task_reward_wei: int,
    policy_name: str,
    decision: str,
    proposed_price_wei: Optional[int] = None,
    estimated_duration_sec: Optional[int] = None,
    reason: str = ""
) -> None:
    """
    Log bid decision in standardized format.
    
    Args:
        agent_name: Name of the bidding agent
        task_id: Task ID being evaluated
        task_capability: Required capability for the task
        task_reward_wei: Task reward in wei
        policy_name: Active bidding policy
        decision: "BID" or "SKIP"
        proposed_price_wei: Proposed bid price (if bidding)
        estimated_duration_sec: Estimated duration (if bidding)
        reason: One-sentence explanation
    """
    task_reward_eth = task_reward_wei / 1e18
    
    fields = {
        "found_task": f"Task #{task_id}",
        "capability": task_capability,
        "reward": f"{task_reward_eth:.6f} ETH ({task_reward_wei} wei)",
        "policy": policy_name,
        "decision": decision,
    }
    
    if proposed_price_wei is not None:
        price_eth = proposed_price_wei / 1e18
        price_pct = (proposed_price_wei / task_reward_wei * 100) if task_reward_wei > 0 else 0
        fields["proposed_price"] = f"{price_eth:.6f} ETH ({price_pct:.1f}% of reward)"
    
    if estimated_duration_sec is not None:
        fields["estimated_duration"] = f"{estimated_duration_sec} seconds"
    
    if reason:
        fields["reason"] = reason
    
    log_decision(agent_name, "Bid Decision", **fields)


def log_worker_selection(
    agent_name: str,
    task_id: int,
    task_capability: str,
    task_reward_wei: int,
    candidates: list[Dict[str, Any]],
    policy_name: str,
    risk_tolerance: float,
    selected_worker: Optional[str] = None,
    selected_bid_id: Optional[int] = None,
    selected_score: Optional[float] = None,
    reason: str = ""
) -> None:
    """
    Log worker selection decision in standardized format.
    
    Args:
        agent_name: Name of the buyer agent
        task_id: Task ID being assigned
        task_capability: Required capability
        task_reward_wei: Task reward in wei
        candidates: List of candidate dicts with keys: bidder, bid_id, score, reputation, price_wei, duration_sec
        policy_name: Active selection policy
        risk_tolerance: Minimum acceptable score threshold
        selected_worker: Address of selected worker (if any)
        selected_bid_id: ID of selected bid (if any)
        selected_score: Score of selected bid (if any)
        reason: One-sentence explanation
    """
    task_reward_eth = task_reward_wei / 1e18
    
    # Format candidates list
    candidate_lines = []
    for i, candidate in enumerate(candidates, 1):
        bidder = candidate.get("bidder", "Unknown")
        bid_id = candidate.get("bid_id", 0)
        score = candidate.get("score", 0.0)
        rep = candidate.get("reputation", 50)
        price_wei = candidate.get("price_wei", 0)
        duration = candidate.get("duration_sec", 0)
        
        price_eth = price_wei / 1e18
        price_pct = (price_wei / task_reward_wei * 100) if task_reward_wei > 0 else 0
        
        marker = "👑" if selected_bid_id and bid_id == selected_bid_id else f"#{i}"
        
        candidate_lines.append(
            f"{marker} Bid #{bid_id} | Worker: {bidder[:10]}... | "
            f"Score: {score:.2f} | Rep: {rep} | "
            f"Price: {price_eth:.6f} ETH ({price_pct:.1f}%) | "
            f"Duration: {duration}s"
        )
    
    fields = {
        "found_task": f"Task #{task_id}",
        "capability": task_capability,
        "reward": f"{task_reward_eth:.6f} ETH ({task_reward_wei} wei)",
        "candidates": candidate_lines,
        "policy": policy_name,
        "risk_tolerance": f"{risk_tolerance} (minimum acceptable score)",
    }
    
    if selected_worker:
        fields["decision"] = f"Selected Worker {selected_worker[:10]}... (Bid #{selected_bid_id})"
        if selected_score is not None:
            fields["selection_score"] = f"{selected_score:.2f}/100"
    else:
        fields["decision"] = "No worker selected (no acceptable bids)"
    
    if reason:
        fields["reason"] = reason
    
    log_decision(agent_name, "Worker Selection", **fields)


def log_verification_result(
    agent_name: str,
    task_id: int,
    worker_address: str,
    verification_passed: bool,
    computed_hash: str,
    submitted_hash: str,
    reason: str = ""
) -> None:
    """
    Log verification result in standardized format.
    
    Args:
        agent_name: Name of the verifier agent
        task_id: Task ID being verified
        worker_address: Address of worker who submitted result
        verification_passed: Whether verification passed
        computed_hash: Hash computed by verifier
        submitted_hash: Hash submitted by worker
        reason: One-sentence explanation
    """
    result = "✅ PASS" if verification_passed else "❌ FAIL"
    hash_match = "✓ Match" if computed_hash == submitted_hash else "✗ Mismatch"
    
    fields = {
        "task_id": f"Task #{task_id}",
        "worker": f"{worker_address[:10]}...",
        "result": result,
        "hash_comparison": hash_match,
        "submitted_hash": submitted_hash,
        "computed_hash": computed_hash,
    }
    
    if reason:
        fields["reason"] = reason
    
    log_decision(agent_name, "Verification Result", **fields)


def log_reputation_change(
    agent_name: str,
    worker_address: str,
    task_id: int,
    change_type: str,
    old_score: int,
    new_score: int,
    old_completed: int,
    new_completed: int,
    old_failed: int,
    new_failed: int,
    stake_change_wei: int = 0,
    reason: str = ""
) -> None:
    """
    Log reputation change in standardized format.
    
    Args:
        agent_name: Name of agent logging the change
        worker_address: Address of worker whose reputation changed
        task_id: Task that triggered the change
        change_type: "Task Pass" or "Task Fail"
        old_score: Previous reputation score
        new_score: New reputation score
        old_completed: Previous completed tasks count
        new_completed: New completed tasks count
        old_failed: Previous failed tasks count
        new_failed: New failed tasks count
        stake_change_wei: Stake change (negative for slash)
        reason: One-sentence explanation
    """
    score_delta = new_score - old_score
    score_direction = "↑" if score_delta > 0 else "↓" if score_delta < 0 else "→"
    
    fields = {
        "worker": f"{worker_address[:10]}...",
        "task_id": f"Task #{task_id}",
        "change_type": change_type,
        "reputation_score": f"{old_score} {score_direction} {new_score} (Δ{score_delta:+d})",
        "completed_tasks": f"{old_completed} → {new_completed}",
        "failed_tasks": f"{old_failed} → {new_failed}",
    }
    
    if stake_change_wei != 0:
        stake_eth = abs(stake_change_wei) / 1e18
        stake_direction = "slashed" if stake_change_wei < 0 else "gained"
        fields["stake_change"] = f"{stake_eth:.6f} ETH {stake_direction}"
    
    if reason:
        fields["reason"] = reason
    
    log_decision(agent_name, "Reputation Change", **fields)
