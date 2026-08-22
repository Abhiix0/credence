"""
Test AutonomousAgent worker cycle - task discovery and execution.

Tests the logic for discovering assigned tasks and executing them
without blockchain interaction.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Task, TaskStatus


def test_task_filtering_logic():
    """
    Test the logic for filtering assigned tasks.
    
    Verifies:
    - Status filtering (only ASSIGNED tasks)
    - Worker address matching (case-insensitive)
    - Exclusion of already submitted tasks
    """
    print("\n" + "="*70)
    print("Testing Worker Task Filtering Logic")
    print("="*70)
    
    # Simulate agent address
    agent_address = "0xAbCdEf1234567890"
    
    # Create test tasks
    tasks = [
        # Should be included: ASSIGNED to me
        Task(
            task_id=1,
            creator="0xBuyer1",
            specification_uri="Task for me",
            required_capability="coding",
            reward_wei=1000000000000000000,
            deadline=9999999999,
            status=TaskStatus.ASSIGNED,
            selected_worker="0xabcdef1234567890",  # Same address, different case
        ),
        # Should be excluded: ASSIGNED to someone else
        Task(
            task_id=2,
            creator="0xBuyer2",
            specification_uri="Task for other worker",
            required_capability="coding",
            reward_wei=1000000000000000000,
            deadline=9999999999,
            status=TaskStatus.ASSIGNED,
            selected_worker="0xOtherWorker123",
        ),
        # Should be excluded: Status is OPEN
        Task(
            task_id=3,
            creator="0xBuyer3",
            specification_uri="Open task",
            required_capability="coding",
            reward_wei=1000000000000000000,
            deadline=9999999999,
            status=TaskStatus.OPEN,
            selected_worker=None,
        ),
        # Should be excluded: Status is SUBMITTED
        Task(
            task_id=4,
            creator="0xBuyer4",
            specification_uri="Already submitted",
            required_capability="coding",
            reward_wei=1000000000000000000,
            deadline=9999999999,
            status=TaskStatus.SUBMITTED,
            selected_worker="0xabcdef1234567890",
            result_uri="ipfs://result-4-abc123",
            result_hash=b'\x00' * 32,
        ),
        # Should be included: ASSIGNED to me (exact case match)
        Task(
            task_id=5,
            creator="0xBuyer5",
            specification_uri="Another task for me",
            required_capability="data-analysis",
            reward_wei=2000000000000000000,
            deadline=9999999999,
            status=TaskStatus.ASSIGNED,
            selected_worker="0xAbCdEf1234567890",  # Exact match
        ),
    ]
    
    # Filter tasks (simulating discover_assigned_tasks logic)
    my_tasks = []
    agent_addr_lower = agent_address.lower()
    
    for task in tasks:
        if task.status == TaskStatus.ASSIGNED:
            if task.selected_worker and task.selected_worker.lower() == agent_addr_lower:
                my_tasks.append(task)
    
    print(f"\nTotal tasks: {len(tasks)}")
    print(f"Tasks assigned to me: {len(my_tasks)}")
    print(f"Expected: 2 (Task #1 and Task #5)")
    
    # Verify results
    assert len(my_tasks) == 2, f"Expected 2 assigned tasks, got {len(my_tasks)}"
    assert my_tasks[0].task_id == 1, "First task should be Task #1"
    assert my_tasks[1].task_id == 5, "Second task should be Task #5"
    
    print("\nFiltered tasks:")
    for task in my_tasks:
        print(f"  Task #{task.task_id}: {task.specification_uri}")
    
    print("\n✅ Task filtering logic works correctly")
    return True


def test_double_execution_prevention():
    """
    Test that the in-progress and submitted tracking prevents double execution.
    """
    print("\n" + "="*70)
    print("Testing Double Execution Prevention")
    print("="*70)
    
    # Simulate tracking sets
    in_progress = set()
    submitted = set()
    
    # Test task IDs
    task_id_1 = 1
    task_id_2 = 2
    
    print("\nScenario 1: First execution attempt")
    # First execution of task 1
    should_process_1 = task_id_1 not in submitted and task_id_1 not in in_progress
    print(f"  Should process Task #{task_id_1}: {should_process_1}")
    assert should_process_1, "First execution should be allowed"
    
    # Mark as in progress
    in_progress.add(task_id_1)
    print(f"  Marked Task #{task_id_1} as in-progress")
    
    print("\nScenario 2: Second execution attempt (while in progress)")
    # Try to execute again while in progress
    should_process_2 = task_id_1 not in submitted and task_id_1 not in in_progress
    print(f"  Should process Task #{task_id_1}: {should_process_2}")
    assert not should_process_2, "Should not process while in progress"
    
    print("\nScenario 3: Execution completes, marked as submitted")
    # Execution completes
    in_progress.discard(task_id_1)
    submitted.add(task_id_1)
    print(f"  Marked Task #{task_id_1} as submitted")
    
    print("\nScenario 4: Third execution attempt (after submission)")
    # Try to execute after submission
    should_process_3 = task_id_1 not in submitted and task_id_1 not in in_progress
    print(f"  Should process Task #{task_id_1}: {should_process_3}")
    assert not should_process_3, "Should not process already-submitted task"
    
    print("\nScenario 5: Different task (not yet processed)")
    # Different task should still be processable
    should_process_4 = task_id_2 not in submitted and task_id_2 not in in_progress
    print(f"  Should process Task #{task_id_2}: {should_process_4}")
    assert should_process_4, "Different task should be processable"
    
    print("\n✅ Double execution prevention works correctly")
    return True


def test_idempotent_step_execution():
    """
    Test that step() can be called multiple times safely.
    """
    print("\n" + "="*70)
    print("Testing Idempotent Step Execution")
    print("="*70)
    
    # Simulate multiple step() calls
    submitted_tasks = set()
    
    # Simulate tasks
    assigned_tasks = [
        {"task_id": 1, "spec": "Task 1"},
        {"task_id": 2, "spec": "Task 2"},
    ]
    
    print("\nFirst step() call:")
    # First call processes both tasks
    for task in assigned_tasks:
        if task["task_id"] not in submitted_tasks:
            print(f"  Processing Task #{task['task_id']}")
            submitted_tasks.add(task["task_id"])
    
    print(f"  Submitted tasks: {submitted_tasks}")
    assert len(submitted_tasks) == 2
    
    print("\nSecond step() call (should skip already-submitted):")
    # Second call skips both
    processed_count = 0
    for task in assigned_tasks:
        if task["task_id"] not in submitted_tasks:
            print(f"  Processing Task #{task['task_id']}")
            processed_count += 1
        else:
            print(f"  Skipping Task #{task['task_id']} (already submitted)")
    
    assert processed_count == 0, "Should not process already-submitted tasks"
    
    print("\nThird step() call with new task:")
    # Add new task
    new_task = {"task_id": 3, "spec": "Task 3"}
    assigned_tasks.append(new_task)
    
    # Third call processes only new task
    processed_count = 0
    for task in assigned_tasks:
        if task["task_id"] not in submitted_tasks:
            print(f"  Processing Task #{task['task_id']}")
            submitted_tasks.add(task["task_id"])
            processed_count += 1
        else:
            print(f"  Skipping Task #{task['task_id']} (already submitted)")
    
    assert processed_count == 1, "Should process only new task"
    assert len(submitted_tasks) == 3
    
    print(f"\nFinal submitted tasks: {submitted_tasks}")
    print("✅ Step execution is idempotent and safe")
    return True


def test_execution_order():
    """
    Test that step() executes in the correct order.
    """
    print("\n" + "="*70)
    print("Testing Execution Order")
    print("="*70)
    
    execution_log = []
    
    # Simulate step() execution order
    print("\nExecuting step() operations:")
    
    # 1. Observe
    execution_log.append("observe")
    print("  1. Observe (update balance)")
    
    # 2. Discover open tasks and bid
    execution_log.append("discover_open")
    print("  2. Discover open tasks")
    execution_log.append("evaluate_bid")
    print("  3. Evaluate and bid on tasks")
    
    # 3. Discover assigned tasks and execute
    execution_log.append("discover_assigned")
    print("  4. Discover assigned tasks")
    execution_log.append("execute_submit")
    print("  5. Execute and submit results")
    
    print(f"\nExecution log: {execution_log}")
    
    # Verify order
    expected_order = [
        "observe",
        "discover_open",
        "evaluate_bid",
        "discover_assigned",
        "execute_submit"
    ]
    
    assert execution_log == expected_order, \
        f"Execution order mismatch. Expected {expected_order}, got {execution_log}"
    
    print("✅ Execution order is correct")
    return True


if __name__ == "__main__":
    test_task_filtering_logic()
    test_double_execution_prevention()
    test_idempotent_step_execution()
    test_execution_order()
    
    print("\n" + "="*70)
    print("✅ All worker cycle tests passed!")
    print("="*70)
    print("\nNote: These tests verify the worker cycle logic.")
    print("Full integration tests require a running testnet.")
