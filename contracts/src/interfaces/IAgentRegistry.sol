// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IAgentRegistry {
    struct Agent {
        address wallet;
        string name;
        string[] capabilities;
        uint256 reputationScore;
        uint256 completedTasks;
        uint256 failedTasks;
        bool isRegistered;
    }

    event AgentRegistered(address indexed wallet, string name, string[] capabilities);
    event CapabilitiesUpdated(address indexed wallet, string[] capabilities);
    event ReputationUpdated(address indexed wallet, uint256 newScore, bool success);

    function registerAgent(string calldata name, string[] calldata capabilities) external;
    function updateCapabilities(string[] calldata capabilities) external;
    function updateReputation(address agent, bool success) external;
    function getAgent(address agent) external view returns (Agent memory);
    function isRegisteredAgent(address agent) external view returns (bool);
}
