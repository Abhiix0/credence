#!/usr/bin/env python3
"""
End-to-End Integration Test for Credence Autonomous Agent Economy

Tests the complete flow:
1. Agent Registration
2. Task Creation
3. Bid Submission (with stake)
4. Worker Selection  
5. Result Submission
6. Verification & Settlement
7. Reputation Update
8. Expiry Flow (for unfinished tasks)

This script requires deployed contracts and funded wallets.
Set environment variables:
- MONAD_RPC_URL
- PRIVATE_KEY (buyer wallet)
- WORKER_PRIVATE_KEY (worker agent wallet)
- TASK_MARKET_CONTRACT_ADDRESS
- AGENT_REGISTRY_CONTRACT_ADDRESS
"""

import os
import time
from web3 import Web3
from src.wallet.signer import WalletSigner
from src.market.task_market import TaskMarketClient
from src.market.agent_registry import AgentRegistryClient

def test_end_to_end_integration():
    """Test complete agent economy flow."""
    
    print("=== Credence E2E Integration Test ===\n")
    
    # Setup
    rpc_url = os.getenv("MONAD_RPC_URL", "https://testnet-rpc.monad.xyz")
    buyer_key = os.getenv("PRIVATE_KEY")
    worker_key = os.getenv("WORKER_PRIVATE_KEY")
    
    if not buyer_key or not worker_key:
        print("ERROR: PRIVATE_KEY and WORKER_PRIVATE_KEY must be set")
        return False
    
    # Initialize clients
    buyer_signer = WalletSigner(rpc_url, buyer_key)
    worker_signer = WalletSigner(rpc_url, worker_key)
    
    market_buyer = TaskMarketClient(buyer_signer)
    market_worker = TaskMarketClient(worker_signer)
    registry_worker = AgentRegistryClient(worker_signer)
    registry_buyer = AgentRegistryClient(buyer_signer)
    
    print(f"Buyer Address: {buyer_signer.address}")
    print(f"Worker Address: {worker_signer.address}")
    print(f"TaskMarket: {market_buyer.contract_address}")
    print(f"AgentRegistry: {registry_worker.contract_address}\n")
    
    # Step 1: Agent Registration
    print("Step 1: Registering Worker Agent...")
    if not registry_worker.is_registered(worker_signer.address):
        tx_hash = registry_worker.register_agent(
            "TestWorkerAgent",
            ["data-analysis", "computation"]
        )
        if tx_hash:
            print(f"✓ Agent registered: {tx_hash}")
            time.sleep(2)
        else:
            print("✗ Agent registration failed")
            return False
    else:
        print("✓ Agent already registered")
    
    # Verify registration
    reputation = registry_buyer.get_agent_reputation(worker_signer.address)
    if reputation:
        print(f"  Reputation Score: {reputation.score}")
        print(f"  Completed: {reputation.completed_tasks}, Failed: {reputation.failed_tasks}\n")
    
    # Step 2: Task Creation
    print("Step 2: Creating Task...")
    deadline = int(time.time()) + 3600  # 1 hour from now
    reward_wei = Web3.to_wei(0.1, 'ether')
    
    tx_hash = market_buyer.create_task(
        spec_uri="ipfs://QmTest",
        required_capability="data-analysis",
        deadline=deadline,
        reward_wei=reward_wei
    )
    
    if not tx_hash:
        print("✗ Task creation failed")
        return False
    
    print(f"✓ Task created: {tx_hash}")
    time.sleep(2)
    
    # Find the task
    tasks = market_worker.fetch_open_tasks()
    if not tasks:
        print("✗ No open tasks found")
        return False
    
    task = tasks[-1]  # Get the latest task
    print(f"  Task ID: {task.task_id}")
    print(f"  Reward: {Web3.from_wei(task.reward_wei, 'ether')} ETH")
    print(f"  Capability: {task.required_capability}\n")
    
    # Step 3: Bid Submission with Stake
    print("Step 3: Submitting Bid with Stake...")
    proposed_price = Web3.to_wei(0.08, 'ether')
    stake_wei = Web3.to_wei(0.01, 'ether')
    
    tx_hash = market_worker.submit_bid(
        task_id=task.task_id,
        proposed_price=proposed_price,
        estimated_duration=300,
        stake_wei=stake_wei
    )
    
    if not tx_hash:
        print("✗ Bid submission failed")
        return False
    
    print(f"✓ Bid submitted: {tx_hash}")
    print(f"  Proposed Price: {Web3.from_wei(proposed_price, 'ether')} ETH")
    print(f"  Stake: {Web3.from_wei(stake_wei, 'ether')} ETH\n")
    time.sleep(2)
    
    # Fetch bids
    bids = market_buyer.fetch_bids_for_task(task.task_id)
    if not bids:
        print("✗ No bids found")
        return False
    
    bid = bids[-1]
    print(f"  Bid ID: {bid.bid_id}\n")
    
    # Step 4: Worker Selection
    print("Step 4: Selecting Worker...")
    tx_hash = market_buyer.select_worker(task.task_id, bid.bid_id)
    
    if not tx_hash:
        print("✗ Worker selection failed")
        return False
    
    print(f"✓ Worker selected: {tx_hash}\n")
    time.sleep(2)
    
    # Step 5: Result Submission
    print("Step 5: Submitting Result...")
    result_hash = Web3.keccak(text="test result")
    
    tx_hash = market_worker.submit_task_result(
        task_id=task.task_id,
        result_uri="ipfs://QmResult",
        result_hash=result_hash
    )
    
    if not tx_hash:
        print("✗ Result submission failed")
        return False
    
    print(f"✓ Result submitted: {tx_hash}\n")
    time.sleep(2)
    
    # Step 6: Verification & Settlement
    print("Step 6: Verifying Result (PASS)...")
    tx_hash = market_buyer.verify_result(task.task_id, passed=True)
    
    if not tx_hash:
        print("✗ Verification failed")
        return False
    
    print(f"✓ Result verified and settled: {tx_hash}\n")
    time.sleep(2)
    
    # Step 7: Check Reputation Update
    print("Step 7: Checking Reputation Update...")
    reputation = registry_buyer.get_agent_reputation(worker_signer.address)
    
    if reputation:
        print(f"✓ Reputation updated:")
        print(f"  Score: {reputation.score}")
        print(f"  Completed: {reputation.completed_tasks}")
        print(f"  Failed: {reputation.failed_tasks}\n")
    else:
        print("✗ Could not fetch reputation\n")
    
    # Step 8: Test Expiry Flow (create a task and expire it)
    print("Step 8: Testing Expiry Flow...")
    past_deadline = int(time.time()) - 100  # Already expired
    
    tx_hash = market_buyer.create_task(
        spec_uri="ipfs://QmExpireTest",
        required_capability="test",
        deadline=past_deadline,
        reward_wei=Web3.to_wei(0.05, 'ether')
    )
    
    if tx_hash:
        print(f"✓ Expiry test task created: {tx_hash}")
        time.sleep(2)
        
        # Get the task ID
        tasks = market_buyer.fetch_open_tasks()
        if tasks:
            expire_task = tasks[-1]
            
            # Try to expire it
            tx_hash = market_buyer.expire_task(expire_task.task_id)
            if tx_hash:
                print(f"✓ Task expired successfully: {tx_hash}\n")
            else:
                print("✗ Task expiry failed\n")
    
    print("=== E2E Integration Test Complete ===")
    return True

if __name__ == "__main__":
    success = test_end_to_end_integration()
    exit(0 if success else 1)
