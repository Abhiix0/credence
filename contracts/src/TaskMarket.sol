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

    function submitBid(
        uint256 taskId,
        uint256 proposedPrice,
        uint256 estimatedDuration
    ) external override returns (uint256) {
        Task storage task = _tasks[taskId];
        require(task.status == TaskStatus.Open, "Task is not open");
        require(block.timestamp < task.deadline, "Task deadline passed");
        require(proposedPrice <= task.reward, "Bid exceeds task reward");

        _bidCounter++;
        uint256 bidId = _bidCounter;

        _bids[bidId] = Bid({
            id: bidId,
            taskId: taskId,
            bidder: msg.sender,
            proposedPrice: proposedPrice,
            estimatedDuration: estimatedDuration,
            timestamp: block.timestamp,
            isAccepted: false
        });

        _taskBids[taskId].push(bidId);
        emit BidSubmitted(bidId, taskId, msg.sender, proposedPrice, estimatedDuration);
        return bidId;
    }

    function selectWorker(uint256 taskId, uint256 bidId) external override {
        Task storage task = _tasks[taskId];
        require(msg.sender == task.creator, "Only task creator can select worker");
        require(task.status == TaskStatus.Open, "Task not open");

        Bid storage bid = _bids[bidId];
        require(bid.taskId == taskId, "Bid does not belong to task");

        task.status = TaskStatus.Assigned;
        task.selectedWorker = bid.bidder;
        task.acceptedBidId = bidId;
        bid.isAccepted = true;

        emit WorkerSelected(taskId, bidId, bid.bidder);
    }

    function submitResult(
        uint256 taskId,
        string calldata resultUri,
        bytes32 resultHash
    ) external override {
        Task storage task = _tasks[taskId];
        require(task.status == TaskStatus.Assigned, "Task not assigned");
        require(msg.sender == task.selectedWorker, "Only assigned worker can submit result");
        require(block.timestamp <= task.deadline, "Task deadline exceeded");

        task.status = TaskStatus.Submitted;
        task.resultUri = resultUri;
        task.resultHash = resultHash;

        emit ResultSubmitted(taskId, msg.sender, resultUri, resultHash);
    }

    function verifyResult(uint256 taskId, bool passed) external override {
        Task storage task = _tasks[taskId];
        require(msg.sender == task.creator || msg.sender == owner, "Unauthorized verifier");
        require(task.status == TaskStatus.Submitted, "Result not submitted");

        Bid memory acceptedBid = _bids[task.acceptedBidId];
        uint256 payment = acceptedBid.proposedPrice > 0 ? acceptedBid.proposedPrice : task.reward;
        uint256 refund = task.reward > payment ? task.reward - payment : 0;

        if (passed) {
            task.status = TaskStatus.VerifiedPass;
            
            // Pay worker
            (bool successWorker, ) = payable(task.selectedWorker).call{value: payment}("");
            require(successWorker, "Worker transfer failed");

            // Refund any excess reward to creator
            if (refund > 0) {
                (bool successRefund, ) = payable(task.creator).call{value: refund}("");
                require(successRefund, "Refund transfer failed");
            }

            if (address(registry) != address(0)) {
                registry.updateReputation(task.selectedWorker, true);
            }

            emit TaskSettled(taskId, task.selectedWorker, payment, true);
        } else {
            task.status = TaskStatus.VerifiedFail;

            // Full refund to creator
            (bool successRefund, ) = payable(task.creator).call{value: task.reward}("");
            require(successRefund, "Refund failed");

            if (address(registry) != address(0)) {
                registry.updateReputation(task.selectedWorker, false);
            }

            emit TaskSettled(taskId, task.creator, task.reward, false);
        }
    }

    function cancelTask(uint256 taskId) external override {
        Task storage task = _tasks[taskId];
        require(msg.sender == task.creator, "Only creator can cancel");
        require(task.status == TaskStatus.Open, "Only open tasks can be cancelled");

        task.status = TaskStatus.Cancelled;
        uint256 refundAmount = task.reward;
        task.reward = 0;

        (bool success, ) = payable(msg.sender).call{value: refundAmount}("");
        require(success, "Cancel refund failed");

        emit TaskCancelled(taskId, msg.sender, refundAmount);
    }

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
