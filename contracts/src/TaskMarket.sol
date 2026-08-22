// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./interfaces/ITaskMarket.sol";
import "./interfaces/IAgentRegistry.sol";

contract TaskMarket is ITaskMarket {
    IAgentRegistry public registry;
    address public owner;

    uint256 private _taskCounter;
    uint256 private _bidCounter;

    mapping(uint256 => Task) private _tasks;
    mapping(uint256 => Bid) private _bids;
    mapping(uint256 => uint256[]) private _taskBids;

    // Tracks whether a non-selected bid's stake has already been refunded
    // to prevent any double-refund. Keyed by bidId.
    mapping(uint256 => bool) private _stakeRefunded;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function setRegistry(address _registry) external onlyOwner {
        registry = IAgentRegistry(_registry);
    }

    // ─────────────────────────────────────────────
    // Task creation — unchanged from P1.1
    // ─────────────────────────────────────────────

    function createTask(
        string calldata specificationUri,
        string calldata requiredCapability,
        uint256 deadline
    ) external payable override returns (uint256) {
        require(msg.value > 0, "Reward must be greater than zero");
        require(deadline > block.timestamp, "Deadline must be in the future");

        _taskCounter++;
        uint256 taskId = _taskCounter;

        _tasks[taskId] = Task({
            id: taskId,
            creator: msg.sender,
            specificationUri: specificationUri,
            requiredCapability: requiredCapability,
            reward: msg.value,
            deadline: deadline,
            status: TaskStatus.Open,
            selectedWorker: address(0),
            acceptedBidId: 0,
            resultUri: "",
            resultHash: bytes32(0)
        });

        emit TaskCreated(taskId, msg.sender, msg.value, requiredCapability, deadline);
        return taskId;
    }

    // ─────────────────────────────────────────────
    // Bidding — now payable; msg.value = stake
    // ─────────────────────────────────────────────

    function submitBid(
        uint256 taskId,
        uint256 proposedPrice,
        uint256 estimatedDuration
    ) external payable override returns (uint256) {
        // P1.1 guards
        Task storage task = _tasks[taskId];
        require(task.creator != address(0), "Task does not exist");
        require(task.status == TaskStatus.Open, "Task is not open");
        require(block.timestamp < task.deadline, "Task deadline passed");
        require(proposedPrice <= task.reward, "Bid exceeds task reward");

        // P1.2: stake must be positive
        require(msg.value > 0, "Stake must be greater than zero");

        _bidCounter++;
        uint256 bidId = _bidCounter;

        _bids[bidId] = Bid({
            id: bidId,
            taskId: taskId,
            bidder: msg.sender,
            proposedPrice: proposedPrice,
            estimatedDuration: estimatedDuration,
            timestamp: block.timestamp,
            isAccepted: false,
            stake: msg.value
        });

        _taskBids[taskId].push(bidId);
        emit BidSubmitted(bidId, taskId, msg.sender, proposedPrice, estimatedDuration);
        return bidId;
    }

    // ─────────────────────────────────────────────
    // Worker selection — refunds non-selected stakes
    // ─────────────────────────────────────────────

    function selectWorker(uint256 taskId, uint256 bidId) external override {
        Task storage task = _tasks[taskId];
        require(task.creator != address(0), "Task does not exist");
        require(msg.sender == task.creator, "Only task creator can select worker");
        require(task.status == TaskStatus.Open, "Task not open");

        Bid storage bid = _bids[bidId];
        require(bid.bidder != address(0), "Bid does not exist");
        require(bid.taskId == taskId, "Bid does not belong to task");
        require(!bid.isAccepted, "Bid already accepted");

        // Effects first
        task.status = TaskStatus.Assigned;
        task.selectedWorker = bid.bidder;
        task.acceptedBidId = bidId;
        bid.isAccepted = true;

        emit WorkerSelected(taskId, bidId, bid.bidder);

        // Refund stakes of all non-selected bids
        uint256[] storage bids = _taskBids[taskId];
        uint256 len = bids.length;
        for (uint256 i = 0; i < len; i++) {
            uint256 otherBidId = bids[i];
            if (otherBidId == bidId) continue;           // skip selected bid
            if (_stakeRefunded[otherBidId]) continue;    // guard against double-refund

            Bid storage otherBid = _bids[otherBidId];
            uint256 refundAmt = otherBid.stake;
            if (refundAmt == 0) continue;

            _stakeRefunded[otherBidId] = true;

            (bool ok, ) = payable(otherBid.bidder).call{value: refundAmt}("");
            require(ok, "Stake refund failed");
        }
    }

    // ─────────────────────────────────────────────
    // Result submission — unchanged from P1.1
    // ─────────────────────────────────────────────

    function submitResult(
        uint256 taskId,
        string calldata resultUri,
        bytes32 resultHash
    ) external override {
        Task storage task = _tasks[taskId];
        require(task.creator != address(0), "Task does not exist");
        require(task.status == TaskStatus.Assigned, "Task not assigned");
        require(msg.sender == task.selectedWorker, "Only assigned worker can submit result");
        require(block.timestamp <= task.deadline, "Task deadline exceeded");

        task.status = TaskStatus.Submitted;
        task.resultUri = resultUri;
        task.resultHash = resultHash;

        emit ResultSubmitted(taskId, msg.sender, resultUri, resultHash);
    }

    // ─────────────────────────────────────────────
    // Verification — updated settlement with stake
    // ─────────────────────────────────────────────

    function verifyResult(uint256 taskId, bool passed) external override {
        Task storage task = _tasks[taskId];
        require(task.creator != address(0), "Task does not exist");
        require(msg.sender == task.creator || msg.sender == owner, "Unauthorized verifier");
        require(task.status == TaskStatus.Submitted, "Result not submitted");

        Bid memory acceptedBid = _bids[task.acceptedBidId];

        // --- Effects ---
        if (passed) {
            task.status = TaskStatus.VerifiedPass;

            // Amounts:
            //   worker payment  = acceptedBid.proposedPrice
            //   worker stake back = acceptedBid.stake
            //   creator refund  = task.reward - acceptedBid.proposedPrice
            uint256 workerPayment  = acceptedBid.proposedPrice;
            uint256 workerStake    = acceptedBid.stake;
            uint256 creatorRefund  = task.reward - workerPayment;

            // --- Interactions ---
            // Pay worker their bid price
            if (workerPayment > 0) {
                (bool okPayment, ) = payable(task.selectedWorker).call{value: workerPayment}("");
                require(okPayment, "Worker payment failed");
            }

            // Return worker's stake
            if (workerStake > 0) {
                (bool okStake, ) = payable(task.selectedWorker).call{value: workerStake}("");
                require(okStake, "Stake return failed");
            }

            // Refund remaining reward to creator
            if (creatorRefund > 0) {
                (bool okRefund, ) = payable(task.creator).call{value: creatorRefund}("");
                require(okRefund, "Creator refund failed");
            }

            if (address(registry) != address(0)) {
                registry.updateReputation(task.selectedWorker, true);
            }

            emit TaskSettled(taskId, task.selectedWorker, workerPayment, true);

        } else {
            task.status = TaskStatus.VerifiedFail;

            uint256 slashedStake = acceptedBid.stake;

            // --- Interactions ---
            // Creator receives full task reward + slashed stake
            uint256 creatorTotal = task.reward + slashedStake;
            (bool okRefund, ) = payable(task.creator).call{value: creatorTotal}("");
            require(okRefund, "Creator refund failed");

            if (address(registry) != address(0)) {
                registry.updateReputation(task.selectedWorker, false);
            }

            if (slashedStake > 0) {
                emit StakeSlashed(taskId, task.acceptedBidId, task.selectedWorker, slashedStake);
            }

            emit TaskSettled(taskId, task.creator, task.reward, false);
        }
    }

    // ─────────────────────────────────────────────
    // Cancellation — unchanged from P1.1
    // Only Open tasks can be cancelled; no stakes exist yet (no bids accepted).
    // Non-selected bid stakes are refunded at selectWorker; cancelled tasks
    // still have Open bids whose stakes remain pending until selectWorker.
    // For simplicity in this stage, cancellation refunds the task reward only.
    // (Worker stakes on open bids for a cancelled task are NOT yet handled —
    //  that is deferred to the expiry stage.)
    // ─────────────────────────────────────────────

    function cancelTask(uint256 taskId) external override {
        Task storage task = _tasks[taskId];
        require(task.creator != address(0), "Task does not exist");
        require(msg.sender == task.creator, "Only creator can cancel");
        require(task.status == TaskStatus.Open, "Only open tasks can be cancelled");

        task.status = TaskStatus.Cancelled;
        uint256 refundAmount = task.reward;
        task.reward = 0;

        // Refund stakes of all submitted bids on this task
        uint256[] storage bids = _taskBids[taskId];
        uint256 len = bids.length;
        for (uint256 i = 0; i < len; i++) {
            uint256 bidId = bids[i];
            if (_stakeRefunded[bidId]) continue;

            Bid storage bid = _bids[bidId];
            uint256 refundAmt = bid.stake;
            if (refundAmt == 0) continue;

            _stakeRefunded[bidId] = true;

            (bool ok, ) = payable(bid.bidder).call{value: refundAmt}("");
            require(ok, "Stake refund failed");
        }

        (bool success, ) = payable(msg.sender).call{value: refundAmount}("");
        require(success, "Cancel refund failed");

        emit TaskCancelled(taskId, msg.sender, refundAmount);
    }

    // ─────────────────────────────────────────────
    // View helpers
    // ─────────────────────────────────────────────

    function getTask(uint256 taskId) external view returns (Task memory) {
        return _tasks[taskId];
    }

    function getBid(uint256 bidId) external view returns (Bid memory) {
        return _bids[bidId];
    }

    function getTaskBids(uint256 taskId) external view returns (uint256[] memory) {
        return _taskBids[taskId];
    }

    function totalTasks() external view returns (uint256) {
        return _taskCounter;
    }
}
