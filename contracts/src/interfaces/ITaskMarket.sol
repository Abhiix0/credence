// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface ITaskMarket {
    enum TaskStatus {
        Open,
        Assigned,
        Submitted,
        VerifiedPass,
        VerifiedFail,
        Cancelled
    }

    struct Task {
        uint256 id;
        address creator;
        string specificationUri;
        string requiredCapability;
        uint256 reward;
        uint256 deadline;
        TaskStatus status;
        address selectedWorker;
        uint256 acceptedBidId;
        string resultUri;
        bytes32 resultHash;
    }

    struct Bid {
        uint256 id;
        uint256 taskId;
        address bidder;
        uint256 proposedPrice;
        uint256 estimatedDuration;
        uint256 timestamp;
        bool isAccepted;
    }

    event TaskCreated(
        uint256 indexed taskId,
        address indexed creator,
        uint256 reward,
        string requiredCapability,
        uint256 deadline
    );
    event BidSubmitted(
        uint256 indexed bidId,
        uint256 indexed taskId,
        address indexed bidder,
        uint256 proposedPrice,
        uint256 estimatedDuration
    );
    event WorkerSelected(uint256 indexed taskId, uint256 indexed bidId, address indexed worker);
    event ResultSubmitted(uint256 indexed taskId, address indexed worker, string resultUri, bytes32 resultHash);
    event TaskSettled(uint256 indexed taskId, address indexed recipient, uint256 amount, bool passed);
    event TaskCancelled(uint256 indexed taskId, address indexed creator, uint256 refundAmount);

    function createTask(
        string calldata specificationUri,
        string calldata requiredCapability,
        uint256 deadline
    ) external payable returns (uint256);

    function submitBid(
        uint256 taskId,
        uint256 proposedPrice,
        uint256 estimatedDuration
    ) external returns (uint256);

    function selectWorker(uint256 taskId, uint256 bidId) external;
    function submitResult(uint256 taskId, string calldata resultUri, bytes32 resultHash) external;
    function verifyResult(uint256 taskId, bool passed) external;
    function cancelTask(uint256 taskId) external;
}
