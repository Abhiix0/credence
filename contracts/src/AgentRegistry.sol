// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "./interfaces/IAgentRegistry.sol";

contract AgentRegistry is IAgentRegistry {
    address public immutable market;
    mapping(address => Agent) private _agents;
    address[] private _registeredAgentList;

    modifier onlyMarket() {
        require(msg.sender == market, "Only TaskMarket can update reputation");
        _;
    }

    constructor(address _market) {
        market = _market;
    }

    function registerAgent(string calldata name, string[] calldata capabilities) external override {
        require(!_agents[msg.sender].isRegistered, "Agent already registered");
        require(bytes(name).length > 0, "Name required");

        _agents[msg.sender] = Agent({
            wallet: msg.sender,
            name: name,
            capabilities: capabilities,
            reputationScore: 100, // Initial baseline score
            completedTasks: 0,
            failedTasks: 0,
            isRegistered: true
        });

        _registeredAgentList.push(msg.sender);
        emit AgentRegistered(msg.sender, name, capabilities);
    }

    function updateCapabilities(string[] calldata capabilities) external override {
        require(_agents[msg.sender].isRegistered, "Agent not registered");
        _agents[msg.sender].capabilities = capabilities;
        emit CapabilitiesUpdated(msg.sender, capabilities);
    }

    function updateReputation(address agent, bool success) external override onlyMarket {
        require(_agents[agent].isRegistered, "Agent not registered");

        if (success) {
            _agents[agent].completedTasks += 1;
            _agents[agent].reputationScore += 10;
        } else {
            _agents[agent].failedTasks += 1;
            if (_agents[agent].reputationScore > 15) {
                _agents[agent].reputationScore -= 15;
            } else {
                _agents[agent].reputationScore = 0;
            }
        }

        emit ReputationUpdated(agent, _agents[agent].reputationScore, success);
    }

    function getAgent(address agent) external view override returns (Agent memory) {
        return _agents[agent];
    }

    function isRegisteredAgent(address agent) external view override returns (bool) {
        return _agents[agent].isRegistered;
    }

    function getAllAgents() external view returns (address[] memory) {
        return _registeredAgentList;
    }
}
