// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/TaskMarket.sol";
import "../src/AgentRegistry.sol";

contract TaskMarketTest is Test {
    TaskMarket market;
    AgentRegistry registry;

    address owner;
    address buyer;
    address worker;
    address worker2;
    address stranger;

    uint256 constant REWARD = 1 ether;
    uint256 constant STAKE  = 0.1 ether;
    uint256 constant HOUR   = 3600;

    receive() external payable {}

    function setUp() public {
        owner    = address(this); // deployer is owner
        buyer    = makeAddr("buyer");
        worker   = makeAddr("worker");
        worker2  = makeAddr("worker2");
        stranger = makeAddr("stranger");

        // Deploy TaskMarket without attaching a registry.
        // The guard `if (address(registry) != address(0))` means reputation
        // calls are skipped, keeping state-machine tests isolated.
        market   = new TaskMarket();
        registry = new AgentRegistry(address(market));
        // Note: setRegistry is NOT called here; registry stays address(0).

        // Fund participants
        vm.deal(buyer,   100 ether);
        vm.deal(worker,   10 ether);
        vm.deal(worker2,  10 ether);
    }

    /// @dev Attach the registry and register `worker` — used by tests that
    ///      exercise the full VerifiedPass / VerifiedFail paths with reputation.
    function _attachRegistryAndRegisterWorker() internal {
        market.setRegistry(address(registry));
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        vm.prank(worker);
        registry.registerAgent("worker-agent", caps);
    }

    // ─────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────

    function _createTask() internal returns (uint256 taskId) {
        vm.prank(buyer);
        taskId = market.createTask{value: REWARD}(
            "ipfs://spec",
            "data-analysis",
            block.timestamp + HOUR
        );
    }

    /// @dev Submit a bid from `worker` with the default STAKE.
    function _submitBid(uint256 taskId) internal returns (uint256 bidId) {
        vm.prank(worker);
        bidId = market.submitBid{value: STAKE}(taskId, REWARD, 60);
    }

    /// @dev Submit a bid from `worker` with explicit stake and proposedPrice.
    function _submitBidWith(
        uint256 taskId,
        address bidder,
        uint256 proposedPrice,
        uint256 stake
    ) internal returns (uint256 bidId) {
        vm.prank(bidder);
        bidId = market.submitBid{value: stake}(taskId, proposedPrice, 60);
    }

    /// @dev Full flow up to Assigned (worker selected, non-selected stakes refunded).
    function _assignTask() internal returns (uint256 taskId, uint256 bidId) {
        taskId = _createTask();
        bidId  = _submitBid(taskId);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
    }

    /// @dev Full flow up to Submitted.
    function _submitResult(uint256 taskId) internal {
        vm.prank(worker);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(1)));
    }

    // ─────────────────────────────────────────────
    // 1. TASK EXISTENCE — nonexistent task rejected
    // ─────────────────────────────────────────────

    function testNonexistentTask_submitBid() public {
        vm.prank(worker);
        vm.expectRevert("Task does not exist");
        market.submitBid{value: STAKE}(999, REWARD, 60);
    }

    function testNonexistentTask_selectWorker() public {
        vm.prank(buyer);
        vm.expectRevert("Task does not exist");
        market.selectWorker(999, 1);
    }

    function testNonexistentTask_submitResult() public {
        vm.prank(worker);
        vm.expectRevert("Task does not exist");
        market.submitResult(999, "ipfs://result", bytes32(0));
    }

    function testNonexistentTask_verifyResult() public {
        vm.prank(buyer);
        vm.expectRevert("Task does not exist");
        market.verifyResult(999, true);
    }

    function testNonexistentTask_cancelTask() public {
        vm.prank(buyer);
        vm.expectRevert("Task does not exist");
        market.cancelTask(999);
    }

    // ─────────────────────────────────────────────
    // 2. TASK CREATION — valid
    // ─────────────────────────────────────────────

    function testCreateTask_valid() public {
        uint256 deadline = block.timestamp + HOUR;
        vm.prank(buyer);
        uint256 taskId = market.createTask{value: REWARD}(
            "ipfs://spec",
            "data-analysis",
            deadline
        );

        ITaskMarket.Task memory t = market.getTask(taskId);
        assertEq(t.id, 1);
        assertEq(t.creator, buyer);
        assertEq(t.reward, REWARD);
        assertEq(t.deadline, deadline);
        assertEq(uint8(t.status), uint8(ITaskMarket.TaskStatus.Open));
    }

    function testCreateTask_rejectsZeroReward() public {
        vm.prank(buyer);
        vm.expectRevert("Reward must be greater than zero");
        market.createTask{value: 0}("ipfs://spec", "cap", block.timestamp + HOUR);
    }

    function testCreateTask_rejectsPastDeadline() public {
        vm.prank(buyer);
        vm.expectRevert("Deadline must be in the future");
        market.createTask{value: REWARD}("ipfs://spec", "cap", block.timestamp);
    }

    // ─────────────────────────────────────────────
    // 3. BIDDING (P1.1 guards preserved)
    // ─────────────────────────────────────────────

    function testSubmitBid_valid() public {
        uint256 taskId = _createTask();
        vm.prank(worker);
        uint256 bidId = market.submitBid{value: STAKE}(taskId, REWARD, 60);

        ITaskMarket.Bid memory b = market.getBid(bidId);
        assertEq(b.taskId, taskId);
        assertEq(b.bidder, worker);
        assertEq(b.proposedPrice, REWARD);
        assertFalse(b.isAccepted);
        assertEq(b.stake, STAKE);
    }

    function testSubmitBid_rejectedAfterAssignment() public {
        (uint256 taskId, ) = _assignTask();

        vm.prank(worker2);
        vm.expectRevert("Task is not open");
        market.submitBid{value: STAKE}(taskId, REWARD, 60);
    }

    function testSubmitBid_rejectedAfterDeadline() public {
        uint256 taskId = _createTask();
        vm.warp(block.timestamp + HOUR + 1);

        vm.prank(worker);
        vm.expectRevert("Task deadline passed");
        market.submitBid{value: STAKE}(taskId, REWARD, 60);
    }

    function testSubmitBid_rejectedAfterCancellation() public {
        uint256 taskId = _createTask();
        vm.prank(buyer);
        market.cancelTask(taskId);

        vm.prank(worker);
        vm.expectRevert("Task is not open");
        market.submitBid{value: STAKE}(taskId, REWARD, 60);
    }

    function testSubmitBid_rejectedAfterVerifiedPass() public {
        _attachRegistryAndRegisterWorker();
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);
        vm.prank(buyer);
        market.verifyResult(taskId, true);

        vm.prank(worker2);
        vm.expectRevert("Task is not open");
        market.submitBid{value: STAKE}(taskId, REWARD, 60);
    }

    function testSubmitBid_rejectedAfterVerifiedFail() public {
        _attachRegistryAndRegisterWorker();
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);
        vm.prank(buyer);
        market.verifyResult(taskId, false);

        vm.prank(worker2);
        vm.expectRevert("Task is not open");
        market.submitBid{value: STAKE}(taskId, REWARD, 60);
    }

    // ─────────────────────────────────────────────
    // 4. WORKER SELECTION (P1.1 guards preserved)
    // ─────────────────────────────────────────────

    function testSelectWorker_valid() public {
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);

        vm.prank(buyer);
        market.selectWorker(taskId, bidId);

        ITaskMarket.Task memory t = market.getTask(taskId);
        assertEq(uint8(t.status), uint8(ITaskMarket.TaskStatus.Assigned));
        assertEq(t.selectedWorker, worker);
        assertEq(t.acceptedBidId, bidId);

        ITaskMarket.Bid memory b = market.getBid(bidId);
        assertTrue(b.isAccepted);
    }

    function testSelectWorker_nonCreatorRejected() public {
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);

        vm.prank(stranger);
        vm.expectRevert("Only task creator can select worker");
        market.selectWorker(taskId, bidId);
    }

    function testSelectWorker_nonexistentBidRejected() public {
        uint256 taskId = _createTask();

        vm.prank(buyer);
        vm.expectRevert("Bid does not exist");
        market.selectWorker(taskId, 9999);
    }

    function testSelectWorker_bidBelongingToOtherTaskRejected() public {
        uint256 taskId1 = _createTask();

        vm.prank(buyer);
        uint256 taskId2 = market.createTask{value: REWARD}(
            "ipfs://spec2",
            "analysis",
            block.timestamp + HOUR
        );

        vm.prank(worker);
        uint256 bidId2 = market.submitBid{value: STAKE}(taskId2, REWARD, 60);

        vm.prank(buyer);
        vm.expectRevert("Bid does not belong to task");
        market.selectWorker(taskId1, bidId2);
    }

    function testSelectWorker_alreadyAcceptedBidRejected() public {
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);

        vm.prank(buyer);
        market.selectWorker(taskId, bidId);

        vm.prank(buyer);
        uint256 taskId2 = market.createTask{value: REWARD}(
            "ipfs://spec2",
            "analysis",
            block.timestamp + HOUR
        );
        vm.prank(worker2);
        uint256 bidId2 = market.submitBid{value: STAKE}(taskId2, REWARD, 60);
        vm.prank(buyer);
        market.selectWorker(taskId2, bidId2);

        // taskId2 is now Assigned — trying to re-select on it should revert "Task not open"
        vm.prank(buyer);
        vm.expectRevert("Task not open");
        market.selectWorker(taskId2, bidId2);
    }

    // ─────────────────────────────────────────────
    // 5. RESULT SUBMISSION (P1.1 unchanged)
    // ─────────────────────────────────────────────

    function testSubmitResult_valid() public {
        (uint256 taskId, ) = _assignTask();

        vm.prank(worker);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(42)));

        ITaskMarket.Task memory t = market.getTask(taskId);
        assertEq(uint8(t.status), uint8(ITaskMarket.TaskStatus.Submitted));
        assertEq(t.resultUri, "ipfs://result");
        assertEq(t.resultHash, bytes32(uint256(42)));
    }

    function testSubmitResult_nonSelectedWorkerRejected() public {
        (uint256 taskId, ) = _assignTask();

        vm.prank(worker2);
        vm.expectRevert("Only assigned worker can submit result");
        market.submitResult(taskId, "ipfs://result", bytes32(0));
    }

    function testSubmitResult_secondSubmissionRejected() public {
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);

        vm.prank(worker);
        vm.expectRevert("Task not assigned");
        market.submitResult(taskId, "ipfs://result2", bytes32(0));
    }

    function testSubmitResult_afterDeadlineRejected() public {
        (uint256 taskId, ) = _assignTask();
        vm.warp(block.timestamp + HOUR + 1);

        vm.prank(worker);
        vm.expectRevert("Task deadline exceeded");
        market.submitResult(taskId, "ipfs://result", bytes32(0));
    }

    // ─────────────────────────────────────────────
    // 6. VERIFICATION (P1.1 guards preserved)
    // ─────────────────────────────────────────────

    function testVerifyResult_passedByCreator() public {
        _attachRegistryAndRegisterWorker();
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);

        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore  = buyer.balance;

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        ITaskMarket.Task memory t = market.getTask(taskId);
        assertEq(uint8(t.status), uint8(ITaskMarket.TaskStatus.VerifiedPass));

        // Worker receives proposedPrice (= REWARD) + stake back
        assertEq(worker.balance, workerBalBefore + REWARD + STAKE, "worker payment+stake");
        // Creator receives remainder (REWARD - REWARD = 0)
        assertEq(buyer.balance, buyerBalBefore, "no creator refund when bid==reward");
    }

    function testVerifyResult_failedByCreator() public {
        _attachRegistryAndRegisterWorker();
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);

        uint256 buyerBalBefore  = buyer.balance;
        uint256 workerBalBefore = worker.balance;

        vm.prank(buyer);
        market.verifyResult(taskId, false);

        ITaskMarket.Task memory t = market.getTask(taskId);
        assertEq(uint8(t.status), uint8(ITaskMarket.TaskStatus.VerifiedFail));

        // Creator gets task reward + slashed stake
        assertEq(buyer.balance, buyerBalBefore + REWARD + STAKE, "creator gets reward+stake");
        // Worker loses stake (balance unchanged since selectWorker)
        assertEq(worker.balance, workerBalBefore, "worker keeps nothing");
    }

    function testVerifyResult_passedByOwner() public {
        _attachRegistryAndRegisterWorker();
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);

        // owner == address(this) (deployer)
        market.verifyResult(taskId, true);

        ITaskMarket.Task memory t = market.getTask(taskId);
        assertEq(uint8(t.status), uint8(ITaskMarket.TaskStatus.VerifiedPass));
    }

    function testVerifyResult_unauthorizedVerifierRejected() public {
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);

        vm.prank(stranger);
        vm.expectRevert("Unauthorized verifier");
        market.verifyResult(taskId, true);
    }

    function testVerifyResult_secondVerificationRejectedAfterPass() public {
        _attachRegistryAndRegisterWorker();
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        vm.prank(buyer);
        vm.expectRevert("Result not submitted");
        market.verifyResult(taskId, false);
    }

    function testVerifyResult_secondVerificationRejectedAfterFail() public {
        _attachRegistryAndRegisterWorker();
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);

        vm.prank(buyer);
        market.verifyResult(taskId, false);

        vm.prank(buyer);
        vm.expectRevert("Result not submitted");
        market.verifyResult(taskId, true);
    }

    function testVerifyResult_rejectsWhenNotSubmitted() public {
        (uint256 taskId, ) = _assignTask();

        vm.prank(buyer);
        vm.expectRevert("Result not submitted");
        market.verifyResult(taskId, true);
    }

    // ─────────────────────────────────────────────
    // 7. CANCELLATION (P1.1 unchanged)
    // ─────────────────────────────────────────────

    function testCancelTask_validOpenTask() public {
        uint256 taskId = _createTask();
        uint256 buyerBalBefore = buyer.balance;

        vm.prank(buyer);
        market.cancelTask(taskId);

        ITaskMarket.Task memory t = market.getTask(taskId);
        assertEq(uint8(t.status), uint8(ITaskMarket.TaskStatus.Cancelled));
        assertEq(t.reward, 0);
        assertEq(buyer.balance, buyerBalBefore + REWARD);
    }

    function testCancelTask_rejectedByNonCreator() public {
        uint256 taskId = _createTask();

        vm.prank(stranger);
        vm.expectRevert("Only creator can cancel");
        market.cancelTask(taskId);
    }

    function testCancelTask_rejectedAfterAssignment() public {
        (uint256 taskId, ) = _assignTask();

        vm.prank(buyer);
        vm.expectRevert("Only open tasks can be cancelled");
        market.cancelTask(taskId);
    }

    function testCancelTask_rejectedAfterVerifiedPass() public {
        _attachRegistryAndRegisterWorker();
        (uint256 taskId, ) = _assignTask();
        _submitResult(taskId);
        vm.prank(buyer);
        market.verifyResult(taskId, true);

        vm.prank(buyer);
        vm.expectRevert("Only open tasks can be cancelled");
        market.cancelTask(taskId);
    }

    // ─────────────────────────────────────────────
    // 8. PARTIAL BID — P1.1 accounting updated for stake
    // ─────────────────────────────────────────────

    function testVerifyResult_partialBid_excessRefundedToBuyer() public {
        _attachRegistryAndRegisterWorker();
        uint256 taskId = _createTask(); // reward = 1 ether

        // Worker bids half price with default stake
        uint256 bidId = _submitBidWith(taskId, worker, 0.5 ether, STAKE);

        vm.prank(buyer);
        market.selectWorker(taskId, bidId);

        _submitResult(taskId);

        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore  = buyer.balance;

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // Worker gets 0.5 ether payment + STAKE back
        assertEq(worker.balance, workerBalBefore + 0.5 ether + STAKE, "worker paid + stake returned");
        // Creator gets 0.5 ether back (excess reward)
        assertEq(buyer.balance, buyerBalBefore + 0.5 ether, "excess refunded to buyer");
    }

    // ═══════════════════════════════════════════════════════════════════
    // P1.2 — WORKER STAKE TESTS
    // ═══════════════════════════════════════════════════════════════════

    // ─────────────────────────────────────────────
    // 9. STAKE CREATION
    // ─────────────────────────────────────────────

    function testStake_zeroStakeReverts() public {
        uint256 taskId = _createTask();

        vm.prank(worker);
        vm.expectRevert("Stake must be greater than zero");
        market.submitBid{value: 0}(taskId, REWARD, 60);
    }

    function testStake_storesCorrectAmount() public {
        uint256 taskId = _createTask();
        uint256 myStake = 0.25 ether;

        vm.prank(worker);
        uint256 bidId = market.submitBid{value: myStake}(taskId, REWARD, 60);

        ITaskMarket.Bid memory b = market.getBid(bidId);
        assertEq(b.stake, myStake, "stored stake matches msg.value");
    }

    function testStake_proposedPriceCanBeLessThanStake() public {
        uint256 taskId = _createTask();
        uint256 bigStake = 0.5 ether;
        uint256 smallPrice = 0.1 ether;

        vm.prank(worker);
        uint256 bidId = market.submitBid{value: bigStake}(taskId, smallPrice, 60);

        ITaskMarket.Bid memory b = market.getBid(bidId);
        assertEq(b.proposedPrice, smallPrice);
        assertEq(b.stake, bigStake);
    }

    function testStake_contractReceivesStakeOnBid() public {
        uint256 taskId = _createTask();
        uint256 contractBalBefore = address(market).balance;

        vm.prank(worker);
        market.submitBid{value: STAKE}(taskId, REWARD, 60);

        assertEq(address(market).balance, contractBalBefore + STAKE, "contract holds stake");
    }

    // ─────────────────────────────────────────────
    // 10. SELECTION — stake handling
    // ─────────────────────────────────────────────

    function testStake_selectedBidStakeRemainsLocked() public {
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);

        uint256 workerBalAfterBid  = worker.balance;
        uint256 contractBalAfterBid = address(market).balance;

        vm.prank(buyer);
        market.selectWorker(taskId, bidId);

        // Worker's balance unchanged after selection (stake still locked)
        assertEq(worker.balance, workerBalAfterBid, "worker balance unchanged - stake locked");
        // Contract still holds stake
        assertEq(address(market).balance, contractBalAfterBid, "contract still holds stake");
    }

    function testStake_nonSelectedBidStakeRefunded() public {
        uint256 taskId = _createTask();

        // worker1 bids — will be selected
        uint256 bidId1 = _submitBid(taskId);

        // worker2 bids — should be refunded at selection
        uint256 w2BalAfterBid = worker2.balance;
        vm.prank(worker2);
        market.submitBid{value: STAKE}(taskId, REWARD, 60);
        assertEq(worker2.balance, w2BalAfterBid - STAKE, "worker2 stake deducted");

        vm.prank(buyer);
        market.selectWorker(taskId, bidId1);

        // worker2's stake must be refunded
        assertEq(worker2.balance, w2BalAfterBid, "worker2 stake refunded after selectWorker");

        // worker1's stake still locked
        // (checked by contract balance: reward + worker1 stake remain)
        assertEq(address(market).balance, REWARD + STAKE, "contract holds reward+selected stake only");
    }

    function testStake_multipleNonSelectedBidsRefunded() public {
        uint256 taskId = _createTask();

        // worker is the one who will be selected
        uint256 bidId1 = _submitBid(taskId);

        // worker2 bids
        uint256 w2BalAfterBid = worker2.balance;
        vm.prank(worker2);
        market.submitBid{value: STAKE}(taskId, REWARD, 60);

        // a third bidder
        address bidder3 = makeAddr("bidder3");
        vm.deal(bidder3, 5 ether);
        uint256 b3BalAfterBid = bidder3.balance;
        vm.prank(bidder3);
        market.submitBid{value: STAKE}(taskId, REWARD, 60);

        vm.prank(buyer);
        market.selectWorker(taskId, bidId1);

        // Both non-selected bidders refunded
        assertEq(worker2.balance, w2BalAfterBid, "worker2 refunded");
        assertEq(bidder3.balance, b3BalAfterBid, "bidder3 refunded");

        // Contract holds: REWARD + worker's STAKE only
        assertEq(address(market).balance, REWARD + STAKE, "only selected stake remains");
    }

    function testStake_selectedBidCannotBeDoubleRefunded() public {
        // There is no explicit public refund function for the selected bid —
        // the only paths that disburse the selected stake are verifyResult.
        // We simply verify the state: after selectWorker, selected bid isAccepted=true
        // and stake is non-zero, while _stakeRefunded is implicitly false for the selected bid.
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);

        vm.prank(buyer);
        market.selectWorker(taskId, bidId);

        ITaskMarket.Bid memory b = market.getBid(bidId);
        assertTrue(b.isAccepted, "selected bid accepted");
        assertEq(b.stake, STAKE, "stake still recorded (not refunded)");
    }

    // ─────────────────────────────────────────────
    // 11. SETTLEMENT — VerifiedPass with stake
    // ─────────────────────────────────────────────

    function testSettle_pass_workerReceivesBidPayment() public {
        uint256 taskId = _createTask();
        uint256 price  = 0.6 ether;
        uint256 bidId  = _submitBidWith(taskId, worker, price, STAKE);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 workerBalBefore = worker.balance;
        vm.prank(buyer);
        market.verifyResult(taskId, true);

        assertEq(worker.balance, workerBalBefore + price + STAKE, "worker receives price + stake");
    }

    function testSettle_pass_workerReceivesStakeBack() public {
        uint256 myStake = 0.3 ether;
        uint256 taskId  = _createTask();
        uint256 bidId   = _submitBidWith(taskId, worker, REWARD, myStake);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 workerBalBefore = worker.balance;
        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // Worker gets REWARD (proposedPrice) + myStake back
        assertEq(worker.balance, workerBalBefore + REWARD + myStake, "stake returned on pass");
    }

    function testSettle_pass_creatorReceivesRemainingReward() public {
        uint256 price  = 0.4 ether;    // creator keeps 0.6 ether
        uint256 taskId = _createTask(); // reward = 1 ether
        uint256 bidId  = _submitBidWith(taskId, worker, price, STAKE);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 buyerBalBefore = buyer.balance;
        vm.prank(buyer);
        market.verifyResult(taskId, true);

        assertEq(buyer.balance, buyerBalBefore + (REWARD - price), "creator gets unused reward");
    }

    function testSettle_pass_zeroPriceBidPaysZeroNotFullReward() public {
        // proposedPrice = 0 → worker receives 0 bid payment (not task.reward)
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBidWith(taskId, worker, 0, STAKE);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore  = buyer.balance;
        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // Worker gets only stake back (payment = 0)
        assertEq(worker.balance, workerBalBefore + STAKE, "zero-price: worker gets stake only");
        // Creator gets full reward back
        assertEq(buyer.balance, buyerBalBefore + REWARD, "zero-price: creator gets full reward");
    }

    function testSettle_pass_contractBalanceAfterSettlement() public {
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // Contract should have no residual funds after full settlement
        assertEq(address(market).balance, 0, "contract balance zero after settlement");
    }

    // ─────────────────────────────────────────────
    // 12. SETTLEMENT — VerifiedFail with stake slash
    // ─────────────────────────────────────────────

    function testSettle_fail_creatorReceivesFullReward() public {
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 buyerBalBefore = buyer.balance;
        vm.prank(buyer);
        market.verifyResult(taskId, false);

        assertEq(buyer.balance, buyerBalBefore + REWARD + STAKE, "creator gets reward + slashed stake");
    }

    function testSettle_fail_workerStakeNotReturned() public {
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 workerBalBefore = worker.balance;
        vm.prank(buyer);
        market.verifyResult(taskId, false);

        // Worker gets nothing
        assertEq(worker.balance, workerBalBefore, "worker stake not returned on fail");
    }

    function testSettle_fail_creatorReceivesSlashedStake() public {
        uint256 myStake = 0.25 ether;
        uint256 taskId  = _createTask();
        uint256 bidId   = _submitBidWith(taskId, worker, REWARD, myStake);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 buyerBalBefore = buyer.balance;
        vm.prank(buyer);
        market.verifyResult(taskId, false);

        assertEq(buyer.balance, buyerBalBefore + REWARD + myStake, "slashed stake goes to creator");
    }

    function testSettle_fail_contractBalanceAfterSettlement() public {
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        vm.prank(buyer);
        market.verifyResult(taskId, false);

        assertEq(address(market).balance, 0, "contract balance zero after failed settlement");
    }

    // ─────────────────────────────────────────────
    // 13. ACCOUNTING — no double-refund / no double return
    // ─────────────────────────────────────────────

    function testAccounting_noDoubleStakeReturnOnPass() public {
        // After VerifiedPass, task is in VerifiedPass — calling verifyResult again
        // reverts "Result not submitted", so there is no path to double-return.
        _attachRegistryAndRegisterWorker();
        uint256 taskId = _createTask();
        uint256 bidId  = _submitBid(taskId);
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // Attempt second verification
        vm.prank(buyer);
        vm.expectRevert("Result not submitted");
        market.verifyResult(taskId, true);
    }

    function testAccounting_noDoubleNonSelectedStakeRefund() public {
        // selectWorker can only be called once per task (task becomes Assigned).
        // A second call with the same or different bidId reverts "Task not open".
        uint256 taskId = _createTask();
        uint256 bidId1 = _submitBid(taskId);      // will be selected
        vm.prank(worker2);
        market.submitBid{value: STAKE}(taskId, REWARD, 60); // will be refunded

        uint256 w2BalAfterBid = worker2.balance;
        vm.prank(buyer);
        market.selectWorker(taskId, bidId1);

        // worker2 was refunded once
        assertEq(worker2.balance, w2BalAfterBid + STAKE, "worker2 refunded exactly once");

        // Try to call selectWorker again — must revert
        vm.prank(buyer);
        vm.expectRevert("Task not open");
        market.selectWorker(taskId, bidId1);
    }

    function testAccounting_contractBalanceConsistencyFullFlow() public {
        // Track contract balance at every step to ensure no ETH is created or lost.
        // Flow: createTask → submitBid → selectWorker (w2 refunded) → submitResult → verifyResult(pass)

        uint256 taskId = _createTask();
        assertEq(address(market).balance, REWARD, "after createTask");

        uint256 bidId1 = _submitBid(taskId);       // worker bids STAKE
        assertEq(address(market).balance, REWARD + STAKE, "after submitBid worker");

        vm.prank(worker2);
        market.submitBid{value: STAKE}(taskId, REWARD, 60); // worker2 bids STAKE
        assertEq(address(market).balance, REWARD + STAKE * 2, "after submitBid worker2");

        vm.prank(buyer);
        market.selectWorker(taskId, bidId1); // worker2's STAKE refunded
        assertEq(address(market).balance, REWARD + STAKE, "after selectWorker (w2 refunded)");

        _submitResult(taskId);
        assertEq(address(market).balance, REWARD + STAKE, "after submitResult (unchanged)");

        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore  = buyer.balance;

        vm.prank(buyer);
        market.verifyResult(taskId, true);
        assertEq(address(market).balance, 0, "after verifyResult pass (all disbursed)");

        // bid == reward, so worker gets REWARD + STAKE; creator gets 0
        assertEq(worker.balance, workerBalBefore + REWARD + STAKE, "worker total");
        assertEq(buyer.balance, buyerBalBefore, "buyer unchanged (bid == reward)");
    }

    // ─────────────────────────────────────────────
    // 14. CANCELLATION WITH STAKED BIDS (P1.2 correction)
    // ─────────────────────────────────────────────

    function testCancelTask_withOneStakedBid_refundsStakeAndReward() public {
        uint256 taskId = _createTask();
        uint256 bidId = _submitBid(taskId);

        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore = buyer.balance;
        assertEq(address(market).balance, REWARD + STAKE, "contract holds reward + stake");

        vm.prank(buyer);
        market.cancelTask(taskId);

        // Worker received stake refund
        assertEq(worker.balance, workerBalBefore + STAKE, "worker stake refunded");
        // Buyer received task reward refund
        assertEq(buyer.balance, buyerBalBefore + REWARD, "creator reward refunded");
        // Contract has 0 remaining balance
        assertEq(address(market).balance, 0, "contract balance 0 after cancel");

        ITaskMarket.Task memory t = market.getTask(taskId);
        assertEq(uint8(t.status), uint8(ITaskMarket.TaskStatus.Cancelled));
        assertEq(t.reward, 0);

        ITaskMarket.Bid memory b = market.getBid(bidId);
        assertEq(b.stake, STAKE);
    }

    function testCancelTask_withMultipleStakedBids_refundsEveryStake() public {
        uint256 taskId = _createTask();

        address worker3 = makeAddr("worker3");
        vm.deal(worker3, 10 ether);

        uint256 stake1 = 0.15 ether;
        uint256 stake2 = 0.25 ether;
        uint256 stake3 = 0.35 ether;

        _submitBidWith(taskId, worker, REWARD, stake1);
        _submitBidWith(taskId, worker2, REWARD, stake2);
        _submitBidWith(taskId, worker3, REWARD, stake3);

        uint256 totalStakes = stake1 + stake2 + stake3;
        assertEq(address(market).balance, REWARD + totalStakes, "contract holds reward + all stakes");

        uint256 w1BalBefore = worker.balance;
        uint256 w2BalBefore = worker2.balance;
        uint256 w3BalBefore = worker3.balance;
        uint256 buyerBalBefore = buyer.balance;

        vm.prank(buyer);
        market.cancelTask(taskId);

        assertEq(worker.balance, w1BalBefore + stake1, "worker 1 stake refunded");
        assertEq(worker2.balance, w2BalBefore + stake2, "worker 2 stake refunded");
        assertEq(worker3.balance, w3BalBefore + stake3, "worker 3 stake refunded");
        assertEq(buyer.balance, buyerBalBefore + REWARD, "buyer reward refunded");
        assertEq(address(market).balance, 0, "contract balance 0 after multi-bid cancel");
    }

    function testCancelTask_cannotBeCancelledAgain() public {
        uint256 taskId = _createTask();
        _submitBid(taskId);

        vm.prank(buyer);
        market.cancelTask(taskId);

        vm.prank(buyer);
        vm.expectRevert("Only open tasks can be cancelled");
        market.cancelTask(taskId);
    }

    function testCancelTask_cannotAcceptNewBids() public {
        uint256 taskId = _createTask();
        _submitBid(taskId);

        vm.prank(buyer);
        market.cancelTask(taskId);

        vm.prank(worker2);
        vm.expectRevert("Task is not open");
        market.submitBid{value: STAKE}(taskId, REWARD, 60);
    }

    function testCancelTask_cannotBeAssigned() public {
        uint256 taskId = _createTask();
        uint256 bidId = _submitBid(taskId);

        vm.prank(buyer);
        market.cancelTask(taskId);

        vm.prank(buyer);
        vm.expectRevert("Task not open");
        market.selectWorker(taskId, bidId);
    }

    function testCancelTask_noStakeRefundedTwice() public {
        uint256 taskId = _createTask();
        uint256 bidId = _submitBid(taskId);

        uint256 workerBalBefore = worker.balance;

        vm.prank(buyer);
        market.cancelTask(taskId);

        assertEq(worker.balance, workerBalBefore + STAKE, "worker refunded once");

        // Attempting to select worker or cancel again must revert, preventing duplicate refund
        vm.prank(buyer);
        vm.expectRevert("Task not open");
        market.selectWorker(taskId, bidId);

        vm.prank(buyer);
        vm.expectRevert("Only open tasks can be cancelled");
        market.cancelTask(taskId);

        assertEq(worker.balance, workerBalBefore + STAKE, "worker balance unchanged");
    }

    function testCancelTask_contractBalanceIsCorrectAfterCancellation() public {
        uint256 taskId = _createTask();
        _submitBid(taskId);
        vm.prank(worker2);
        market.submitBid{value: 0.2 ether}(taskId, 0.8 ether, 60);

        assertEq(address(market).balance, REWARD + STAKE + 0.2 ether);

        vm.prank(buyer);
        market.cancelTask(taskId);

        assertEq(address(market).balance, 0, "contract has zero balance remaining");
    }

    // ═══════════════════════════════════════════════════════════════════
    // P1.3 — SETTLEMENT ACCOUNTING HARDENING
    // ═══════════════════════════════════════════════════════════════════

    // ─────────────────────────────────────────────
    // 15. PASS SETTLEMENT ACCOUNTING
    // ─────────────────────────────────────────────

    /// @dev Task reward > bid price: verify exact amounts for worker and creator
    function testAccountingPass_rewardGreaterThanBid_exactPayments() public {
        uint256 taskId = _createTask();           // reward = 1 ether
        uint256 proposedPrice = 0.6 ether;
        uint256 workerStake = 0.15 ether;
        
        uint256 bidId = _submitBidWith(taskId, worker, proposedPrice, workerStake);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore = buyer.balance;
        uint256 contractBalBefore = address(market).balance;

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // Worker receives exactly proposedPrice (0.6 ether)
        // Worker receives exactly their stake back (0.15 ether)
        assertEq(worker.balance, workerBalBefore + proposedPrice + workerStake, 
            "worker receives exactly proposedPrice + stake");
        
        // Creator receives exactly reward - proposedPrice (1 - 0.6 = 0.4 ether)
        assertEq(buyer.balance, buyerBalBefore + (REWARD - proposedPrice), 
            "creator receives exactly reward - proposedPrice");
        
        // Total outgoing ETH equals reward + selected stake
        uint256 totalPaid = (worker.balance - workerBalBefore) + (buyer.balance - buyerBalBefore);
        assertEq(totalPaid, REWARD + workerStake, "total outgoing equals reward + stake");
        
        // No funds remain from that task after settlement
        assertEq(address(market).balance, contractBalBefore - (REWARD + workerStake), 
            "contract paid out exactly reward + stake");
    }

    /// @dev Verify that all funds are accounted for and zero remains for this task
    function testAccountingPass_noFundsRemainAfterSettlement() public {
        uint256 taskId = _createTask();
        uint256 bidId = _submitBid(taskId);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        // Before settlement, contract holds REWARD + STAKE
        assertEq(address(market).balance, REWARD + STAKE);

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // After settlement, contract should have 0 (single task scenario)
        assertEq(address(market).balance, 0, "no funds remain after settlement");
    }

    /// @dev Zero-price bid: worker receives zero payment but gets stake back
    function testAccountingPass_zeroPriceBid_workerGetsStakeOnly() public {
        uint256 taskId = _createTask();
        uint256 zeroBidPrice = 0;
        uint256 workerStake = 0.2 ether;
        
        uint256 bidId = _submitBidWith(taskId, worker, zeroBidPrice, workerStake);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore = buyer.balance;

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // Worker receives zero task payment but receives stake back
        assertEq(worker.balance, workerBalBefore + workerStake, 
            "worker receives only stake on zero-price bid");
        
        // Creator receives full reward back
        assertEq(buyer.balance, buyerBalBefore + REWARD, 
            "creator receives full reward on zero-price bid");
    }

    /// @dev Partial bid: verify exact creator refund
    function testAccountingPass_partialBid_exactCreatorRefund() public {
        uint256 taskId = _createTask();
        uint256 proposedPrice = 0.3 ether;
        uint256 expectedRefund = REWARD - proposedPrice; // 0.7 ether
        
        uint256 bidId = _submitBidWith(taskId, worker, proposedPrice, STAKE);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 buyerBalBefore = buyer.balance;

        vm.prank(buyer);
        market.verifyResult(taskId, true);

        // Verify exact creator refund
        assertEq(buyer.balance, buyerBalBefore + expectedRefund, 
            "creator receives exactly reward - proposedPrice");
    }

    // ─────────────────────────────────────────────
    // 16. FAIL SETTLEMENT ACCOUNTING
    // ─────────────────────────────────────────────

    /// @dev FAIL settlement: creator receives exactly reward + slashed stake
    function testAccountingFail_creatorReceivesExactAmounts() public {
        uint256 taskId = _createTask();
        uint256 workerStake = 0.2 ether;
        
        uint256 bidId = _submitBidWith(taskId, worker, REWARD, workerStake);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 buyerBalBefore = buyer.balance;
        uint256 workerBalBefore = worker.balance;

        vm.prank(buyer);
        market.verifyResult(taskId, false);

        // Creator receives exactly task reward
        // Creator receives exactly selected worker's slashed stake
        assertEq(buyer.balance, buyerBalBefore + REWARD + workerStake, 
            "creator receives exactly reward + slashed stake");
        
        // Worker receives no stake back
        assertEq(worker.balance, workerBalBefore, "worker receives nothing on fail");
    }

    /// @dev FAIL: total outgoing equals reward + stake
    function testAccountingFail_totalOutgoingEqualsRewardPlusStake() public {
        uint256 taskId = _createTask();
        uint256 workerStake = 0.18 ether;
        
        uint256 bidId = _submitBidWith(taskId, worker, 0.5 ether, workerStake);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        uint256 buyerBalBefore = buyer.balance;
        uint256 contractBalBefore = address(market).balance;

        vm.prank(buyer);
        market.verifyResult(taskId, false);

        // Total outgoing ETH equals reward + selected stake
        uint256 totalPaid = buyer.balance - buyerBalBefore;
        assertEq(totalPaid, REWARD + workerStake, "total outgoing equals reward + stake");
        
        // Contract paid out exactly reward + stake
        assertEq(address(market).balance, contractBalBefore - (REWARD + workerStake), 
            "contract paid exactly reward + stake");
    }

    /// @dev FAIL: no funds remain after settlement
    function testAccountingFail_noFundsRemainAfterSettlement() public {
        uint256 taskId = _createTask();
        uint256 bidId = _submitBid(taskId);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        _submitResult(taskId);

        vm.prank(buyer);
        market.verifyResult(taskId, false);

        // No funds remain (single task scenario)
        assertEq(address(market).balance, 0, "no funds remain after fail settlement");
    }

    // ─────────────────────────────────────────────
    // 17. MULTIPLE SIMULTANEOUS TASKS
    // ─────────────────────────────────────────────

    /// @dev Settle Task A while Task B remains active — split to avoid stack-too-deep
    function testAccountingMultiTask_taskASettlementDoesNotAffectTaskB() public {
        (uint256 taskIdA, uint256 taskIdB) = _multiTaskSetup();
        _multiTaskSettleA(taskIdA);
        _multiTaskSettleB(taskIdB);
    }

    /// @dev Helper: create two tasks, submit bids, select workers, submit result for task A
    function _multiTaskSetup() private returns (uint256 taskIdA, uint256 taskIdB) {
        // Create Task A
        vm.prank(buyer);
        taskIdA = market.createTask{value: 1.5 ether}(
            "ipfs://specA",
            "data-analysis",
            block.timestamp + HOUR
        );
        
        // Create Task B with different amounts
        vm.prank(buyer);
        taskIdB = market.createTask{value: 2.0 ether}(
            "ipfs://specB",
            "data-analysis",
            block.timestamp + HOUR
        );
        
        // Submit bids for both tasks
        uint256 bidIdA = _submitBidWith(taskIdA, worker,  0.9 ether, 0.2 ether);
        uint256 bidIdB = _submitBidWith(taskIdB, worker2, 1.2 ether, 0.3 ether);
        
        // Select workers for both tasks
        vm.prank(buyer);
        market.selectWorker(taskIdA, bidIdA);
        
        vm.prank(buyer);
        market.selectWorker(taskIdB, bidIdB);
        
        // Submit result for Task A only
        vm.prank(worker);
        market.submitResult(taskIdA, "ipfs://resultA", bytes32(uint256(1)));
        
        // Contract holds both tasks' funds: 1.5 + 0.2 + 2.0 + 0.3 = 4.0 ether
        assertEq(address(market).balance, 4.0 ether, "contract holds both tasks' funds");
    }

    /// @dev Helper: settle Task A (PASS) and verify Task B remains intact
    function _multiTaskSettleA(uint256 taskIdA) private {
        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore = buyer.balance;
        uint256 worker2BalBefore = worker2.balance;
        
        // Settle Task A (PASS)
        vm.prank(buyer);
        market.verifyResult(taskIdA, true);
        
        // Verify Task A settlement: worker receives 0.9 + 0.2 = 1.1 ether
        assertEq(worker.balance, workerBalBefore + 1.1 ether, 
            "Task A worker receives correct payment + stake");
        // Buyer receives 1.5 - 0.9 = 0.6 ether
        assertEq(buyer.balance, buyerBalBefore + 0.6 ether, 
            "Task A creator receives correct refund");
        
        // Task B's funds remain: 2.0 + 0.3 = 2.3 ether
        assertEq(address(market).balance, 2.3 ether, 
            "Task B funds remain untouched");
        
        // worker2 balance unchanged (Task B not settled)
        assertEq(worker2.balance, worker2BalBefore, "Task B worker unaffected");
    }

    /// @dev Helper: settle Task B (FAIL) and verify all funds accounted for
    function _multiTaskSettleB(uint256 taskIdB) private {
        vm.prank(worker2);
        market.submitResult(taskIdB, "ipfs://resultB", bytes32(uint256(2)));
        
        uint256 buyerBalBefore = buyer.balance;
        uint256 worker2BalBefore = worker2.balance;
        
        vm.prank(buyer);
        market.verifyResult(taskIdB, false);
        
        // Buyer receives 2.0 + 0.3 = 2.3 ether
        assertEq(buyer.balance, buyerBalBefore + 2.3 ether, 
            "Task B creator receives reward + slashed stake");
        assertEq(worker2.balance, worker2BalBefore, 
            "Task B worker receives nothing on fail");
        assertEq(address(market).balance, 0, 
            "all funds accounted for after both settlements");
    }

    /// @dev Task A cannot consume Task B's escrow
    function testAccountingMultiTask_isolatedTaskAccounting() public {
        // Create two tasks with different rewards
        vm.prank(buyer);
        uint256 taskIdA = market.createTask{value: 1 ether}(
            "ipfs://A", "cap", block.timestamp + HOUR
        );
        
        vm.prank(buyer);
        uint256 taskIdB = market.createTask{value: 3 ether}(
            "ipfs://B", "cap", block.timestamp + HOUR
        );
        
        // Both workers bid
        uint256 bidIdA = _submitBidWith(taskIdA, worker, 1 ether, 0.1 ether);
        uint256 bidIdB = _submitBidWith(taskIdB, worker2, 3 ether, 0.1 ether);
        
        vm.prank(buyer);
        market.selectWorker(taskIdA, bidIdA);
        
        vm.prank(buyer);
        market.selectWorker(taskIdB, bidIdB);
        
        vm.prank(worker);
        market.submitResult(taskIdA, "ipfs://resultA", bytes32(uint256(1)));
        
        // Contract holds: 1 + 0.1 + 3 + 0.1 = 4.2 ether
        assertEq(address(market).balance, 4.2 ether);
        
        // Settle Task A
        vm.prank(buyer);
        market.verifyResult(taskIdA, true);
        
        // Contract should hold exactly Task B's funds
        assertEq(address(market).balance, 3.1 ether, "only Task B funds remain");
        
        // Verify Task B can still be settled correctly
        vm.prank(worker2);
        market.submitResult(taskIdB, "ipfs://resultB", bytes32(uint256(2)));
        
        vm.prank(buyer);
        market.verifyResult(taskIdB, true);
        
        assertEq(address(market).balance, 0, "all funds properly disbursed");
    }

    // ─────────────────────────────────────────────
    // 18. MULTIPLE BIDS ON SAME TASK
    // ─────────────────────────────────────────────

    /// @dev Multiple bids: verify non-selected stakes refunded exactly once
    function testAccountingMultiBid_nonSelectedStakesRefundedOnce() public {
        uint256 taskId = _createTask();
        
        uint256 stake1 = 0.1 ether;
        uint256 stake2 = 0.2 ether;
        uint256 stake3 = 0.15 ether;
        
        // Three workers submit bids
        uint256 bidId1 = _submitBidWith(taskId, worker, REWARD, stake1);
        uint256 bidId2 = _submitBidWith(taskId, worker2, REWARD, stake2);
        
        address worker3 = makeAddr("worker3");
        vm.deal(worker3, 10 ether);
        _submitBidWith(taskId, worker3, REWARD, stake3);
        
        uint256 w2BalBefore = worker2.balance;
        uint256 w3BalBefore = worker3.balance;
        
        // Select worker (bidId1)
        vm.prank(buyer);
        market.selectWorker(taskId, bidId1);
        
        // Non-selected stakes are refunded exactly once
        assertEq(worker2.balance, w2BalBefore + stake2, "worker2 stake refunded exactly once");
        assertEq(worker3.balance, w3BalBefore + stake3, "worker3 stake refunded exactly once");
        
        // Selected stake remains locked
        assertEq(address(market).balance, REWARD + stake1, "selected stake remains locked");
        
        // Complete the task
        vm.prank(worker);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(1)));
        
        vm.prank(buyer);
        market.verifyResult(taskId, true);
        
        // Settlement only accounts for selected worker's stake
        assertEq(address(market).balance, 0, "no stake paid twice");
    }

    /// @dev Verify no stake is accidentally paid twice
    function testAccountingMultiBid_noDoublePayment() public {
        uint256 taskId = _createTask();
        
        uint256 bidId1 = _submitBid(taskId);
        
        vm.prank(worker2);
        market.submitBid{value: STAKE}(taskId, REWARD, 60);
        
        uint256 contractBalBefore = address(market).balance;
        assertEq(contractBalBefore, REWARD + STAKE + STAKE, "contract holds reward + 2 stakes");
        
        // Select worker1
        vm.prank(buyer);
        market.selectWorker(taskId, bidId1);
        
        // worker2's stake was refunded
        assertEq(address(market).balance, REWARD + STAKE, "worker2 stake refunded");
        
        // Settle task
        vm.prank(worker);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(1)));
        
        vm.prank(buyer);
        market.verifyResult(taskId, true);
        
        // All funds accounted for, nothing paid twice
        assertEq(address(market).balance, 0, "no double payment occurred");
    }

    // ─────────────────────────────────────────────
    // 19. DOUBLE SETTLEMENT PROTECTION
    // ─────────────────────────────────────────────

    /// @dev Verify the same task cannot be settled twice
    function testAccountingDoubleSettlement_passCannotBeSettledAgain() public {
        uint256 taskId = _createTask();
        uint256 bidId = _submitBid(taskId);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        
        vm.prank(worker);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(1)));
        
        vm.prank(buyer);
        market.verifyResult(taskId, true);
        
        // Contract should have 0 balance
        assertEq(address(market).balance, 0);
        
        // Attempt to verify again
        vm.prank(buyer);
        vm.expectRevert("Result not submitted");
        market.verifyResult(taskId, true);
        
        // Balance should still be 0 (no double payment)
        assertEq(address(market).balance, 0, "no double settlement occurred");
    }

    /// @dev Verify fail settlement cannot be executed twice
    function testAccountingDoubleSettlement_failCannotBeSettledAgain() public {
        uint256 taskId = _createTask();
        uint256 bidId = _submitBid(taskId);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        
        vm.prank(worker);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(1)));
        
        uint256 buyerBalBefore = buyer.balance;
        
        vm.prank(buyer);
        market.verifyResult(taskId, false);
        
        uint256 buyerPaid = buyer.balance - buyerBalBefore;
        assertEq(buyerPaid, REWARD + STAKE, "buyer received reward + stake");
        
        // Contract has 0 balance
        assertEq(address(market).balance, 0);
        
        // Attempt to verify again
        vm.prank(buyer);
        vm.expectRevert("Result not submitted");
        market.verifyResult(taskId, false);
        
        // Buyer balance unchanged (no double payment)
        assertEq(buyer.balance, buyerBalBefore + REWARD + STAKE, "no double payment to buyer");
        assertEq(address(market).balance, 0, "contract still at 0");
    }

    /// @dev Cannot switch from pass to fail or vice versa
    function testAccountingDoubleSettlement_cannotSwitchVerdict() public {
        uint256 taskId = _createTask();
        uint256 bidId = _submitBid(taskId);
        
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        
        vm.prank(worker);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(1)));
        
        // Verify as PASS
        vm.prank(buyer);
        market.verifyResult(taskId, true);
        
        ITaskMarket.Task memory task = market.getTask(taskId);
        assertEq(uint8(task.status), uint8(ITaskMarket.TaskStatus.VerifiedPass));
        
        // Try to verify as FAIL
        vm.prank(buyer);
        vm.expectRevert("Result not submitted");
        market.verifyResult(taskId, false);
        
        // Status should still be VerifiedPass
        task = market.getTask(taskId);
        assertEq(uint8(task.status), uint8(ITaskMarket.TaskStatus.VerifiedPass));
    }

    // ─────────────────────────────────────────────
    // 20. COMPREHENSIVE FLOW ACCOUNTING
    // Split into private phase helpers to stay within the 16-slot EVM stack
    // limit (no viaIR). Each helper owns its own frame; the public entry point
    // only threads the task/bid IDs between phases.
    // ─────────────────────────────────────────────

    /// @dev Phase 1 — create all three tasks and submit all bids.
    ///      Returns (task1, task2, task3, bid1a, bid2a).
    function _compPhase1_createAndBid()
        private
        returns (
            uint256 task1,
            uint256 task2,
            uint256 task3,
            uint256 bid1a,
            uint256 bid2a
        )
    {
        // Task 1: 2 bids, worker will be selected (PASS)
        vm.prank(buyer);
        task1 = market.createTask{value: 2 ether}("ipfs://spec1", "cap", block.timestamp + HOUR);
        bid1a = _submitBidWith(task1, worker,  1.5 ether, 0.2 ether);
        _submitBidWith(task1, worker2, 1.8 ether, 0.25 ether); // will be refunded at selection

        // Task 2: 1 bid, worker2 selected (FAIL)
        vm.prank(buyer);
        task2 = market.createTask{value: 1 ether}("ipfs://spec2", "cap", block.timestamp + HOUR);
        bid2a = _submitBidWith(task2, worker2, 0.8 ether, 0.1 ether);

        // Task 3: 3 bids, will be cancelled
        vm.prank(buyer);
        task3 = market.createTask{value: 1.5 ether}("ipfs://spec3", "cap", block.timestamp + HOUR);

        address worker3 = makeAddr("worker3");
        vm.deal(worker3, 10 ether);
        _submitBidWith(task3, worker,   1.2 ether, 0.15 ether);
        _submitBidWith(task3, worker2,  1.3 ether, 0.18 ether);
        _submitBidWith(task3, worker3,  1.4 ether, 0.12 ether);

        // Total escrowed: 2.45 + 1.1 + 1.95 = 5.5 ether
        assertEq(address(market).balance, 5.5 ether, "phase1: all funds escrowed");
    }

    /// @dev Phase 2 — select workers, cancel task3. Asserts intermediate balances.
    function _compPhase2_selectAndCancel(
        uint256 task1,
        uint256 task2,
        uint256 task3,
        uint256 bid1a,
        uint256 bid2a
    ) private {
        // Selecting worker for task1 refunds worker2's 0.25 ether stake from that task
        vm.prank(buyer);
        market.selectWorker(task1, bid1a);

        vm.prank(buyer);
        market.selectWorker(task2, bid2a);

        // After selection: 5.5 - 0.25 (worker2 refund from task1) = 5.25 ether
        assertEq(address(market).balance, 5.25 ether, "phase2: non-selected stake refunded");

        // Cancel task3: reward 1.5 + stakes 0.45 leave the contract
        vm.prank(buyer);
        market.cancelTask(task3);

        // 5.25 - 1.95 = 3.3 ether (task1: 2.2 + task2: 1.1)
        assertEq(address(market).balance, 3.3 ether, "phase2: task3 funds refunded");
    }

    /// @dev Phase 3 — settle task1 (PASS) and verify per-task accounting.
    function _compPhase3_settleTask1Pass(uint256 task1) private {
        vm.prank(worker);
        market.submitResult(task1, "ipfs://result1", bytes32(uint256(1)));

        uint256 workerBalBefore = worker.balance;
        uint256 buyerBalBefore  = buyer.balance;

        vm.prank(buyer);
        market.verifyResult(task1, true);

        // worker receives proposedPrice (1.5) + stake (0.2) = 1.7 ether
        assertEq(worker.balance, workerBalBefore + 1.7 ether, "phase3: task1 worker paid");
        // buyer receives reward - proposedPrice = 2 - 1.5 = 0.5 ether
        assertEq(buyer.balance, buyerBalBefore + 0.5 ether,   "phase3: task1 buyer refund");
        // only task2 funds remain: 1 + 0.1 = 1.1 ether
        assertEq(address(market).balance, 1.1 ether, "phase3: only task2 funds remain");
    }

    /// @dev Phase 4 — settle task2 (FAIL) and verify final zero balance.
    function _compPhase4_settleTask2Fail(uint256 task2) private {
        vm.prank(worker2);
        market.submitResult(task2, "ipfs://result2", bytes32(uint256(2)));

        uint256 buyerBalBefore   = buyer.balance;
        uint256 worker2BalBefore = worker2.balance;

        vm.prank(buyer);
        market.verifyResult(task2, false);

        // buyer receives reward (1) + slashed stake (0.1) = 1.1 ether
        assertEq(buyer.balance,   buyerBalBefore   + 1.1 ether, "phase4: task2 buyer gets reward+stake");
        // worker2 receives nothing
        assertEq(worker2.balance, worker2BalBefore,             "phase4: task2 worker gets nothing");
        // all funds properly disbursed
        assertEq(address(market).balance, 0, "phase4: all funds accounted for");
    }

    /// @dev Entry point — threads the four phases together.
    function testAccountingComprehensive_multipleTasksAndBidsFullLifecycle() public {
        (
            uint256 task1,
            uint256 task2,
            uint256 task3,
            uint256 bid1a,
            uint256 bid2a
        ) = _compPhase1_createAndBid();

        _compPhase2_selectAndCancel(task1, task2, task3, bid1a, bid2a);
        _compPhase3_settleTask1Pass(task1);
        _compPhase4_settleTask2Fail(task2);
    }
}
