// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/AgentRegistry.sol";
import "../src/TaskMarket.sol";

contract AgentRegistryTest is Test {
    AgentRegistry registry;
    TaskMarket market;
    
    address owner;
    address agent1;
    address agent2;
    address stranger;
    
    event AgentRegistered(address indexed wallet, string name, string[] capabilities);
    event CapabilitiesUpdated(address indexed wallet, string[] capabilities);
    event ReputationUpdated(address indexed wallet, uint256 newScore, bool success);
    
    function setUp() public {
        owner = address(this);
        agent1 = makeAddr("agent1");
        agent2 = makeAddr("agent2");
        stranger = makeAddr("stranger");
        
        // Deploy TaskMarket first (registry needs market address)
        market = new TaskMarket();
        registry = new AgentRegistry(address(market));
    }
    
    // ═══════════════════════════════════════════════════════════════════
    // AGENT REGISTRATION
    // ═══════════════════════════════════════════════════════════════════
    
    /// @dev Successful agent registration with single capability
    function testRegisterAgent_singleCapability() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.expectEmit(true, false, false, true);
        emit AgentRegistered(agent1, "Agent One", caps);
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.wallet, agent1);
        assertEq(agent.name, "Agent One");
        assertEq(agent.capabilities.length, 1);
        assertEq(agent.capabilities[0], "data-analysis");
        assertEq(agent.reputationScore, 100, "Initial reputation is 100");
        assertEq(agent.completedTasks, 0);
        assertEq(agent.failedTasks, 0);
        assertTrue(agent.isRegistered);
    }
    
    /// @dev Successful agent registration with multiple capabilities
    function testRegisterAgent_multipleCapabilities() public {
        string[] memory caps = new string[](3);
        caps[0] = "data-analysis";
        caps[1] = "machine-learning";
        caps[2] = "blockchain";
        
        vm.prank(agent1);
        registry.registerAgent("Multi-Cap Agent", caps);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.capabilities.length, 3);
        assertEq(agent.capabilities[0], "data-analysis");
        assertEq(agent.capabilities[1], "machine-learning");
        assertEq(agent.capabilities[2], "blockchain");
    }
    
    /// @dev Agent registration with no capabilities is allowed
    function testRegisterAgent_noCapabilities() public {
        string[] memory caps = new string[](0);
        
        vm.prank(agent1);
        registry.registerAgent("No-Cap Agent", caps);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.capabilities.length, 0);
        assertTrue(agent.isRegistered);
    }
    
    /// @dev Cannot register with empty name
    function testRegisterAgent_emptyNameReverts() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        vm.expectRevert("Name required");
        registry.registerAgent("", caps);
    }
    
    /// @dev Cannot register twice
    function testRegisterAgent_duplicateRegistrationReverts() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        // Attempt to register again
        vm.prank(agent1);
        vm.expectRevert("Agent already registered");
        registry.registerAgent("Agent One Updated", caps);
    }
    
    /// @dev Multiple agents can register independently
    function testRegisterAgent_multipleAgentsIndependent() public {
        string[] memory caps1 = new string[](1);
        caps1[0] = "data-analysis";
        
        string[] memory caps2 = new string[](1);
        caps2[0] = "machine-learning";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps1);
        
        vm.prank(agent2);
        registry.registerAgent("Agent Two", caps2);
        
        IAgentRegistry.Agent memory a1 = registry.getAgent(agent1);
        IAgentRegistry.Agent memory a2 = registry.getAgent(agent2);
        
        assertEq(a1.name, "Agent One");
        assertEq(a2.name, "Agent Two");
        assertEq(a1.capabilities[0], "data-analysis");
        assertEq(a2.capabilities[0], "machine-learning");
    }
    
    // ═══════════════════════════════════════════════════════════════════
    // QUERY FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════
    
    /// @dev isRegisteredAgent returns false for unregistered address
    function testIsRegisteredAgent_unregistered() public {
        assertFalse(registry.isRegisteredAgent(stranger));
    }
    
    /// @dev isRegisteredAgent returns true for registered agent
    function testIsRegisteredAgent_registered() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        assertTrue(registry.isRegisteredAgent(agent1));
    }
    
    /// @dev getAgent returns default struct for unregistered address
    function testGetAgent_unregistered() public {
        IAgentRegistry.Agent memory agent = registry.getAgent(stranger);
        assertEq(agent.wallet, address(0));
        assertEq(agent.name, "");
        assertFalse(agent.isRegistered);
    }
    
    /// @dev getAllAgents returns all registered agents
    function testGetAllAgents_multiple() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        vm.prank(agent2);
        registry.registerAgent("Agent Two", caps);
        
        address[] memory agents = registry.getAllAgents();
        assertEq(agents.length, 2);
        assertEq(agents[0], agent1);
        assertEq(agents[1], agent2);
    }
    
    /// @dev getAllAgents returns empty array when no agents
    function testGetAllAgents_empty() public {
        address[] memory agents = registry.getAllAgents();
        assertEq(agents.length, 0);
    }
    
    // ═══════════════════════════════════════════════════════════════════
    // CAPABILITY UPDATES
    // ═══════════════════════════════════════════════════════════════════
    
    /// @dev Agent can update capabilities
    function testUpdateCapabilities_success() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        // Update capabilities
        string[] memory newCaps = new string[](2);
        newCaps[0] = "machine-learning";
        newCaps[1] = "blockchain";
        
        vm.expectEmit(true, false, false, true);
        emit CapabilitiesUpdated(agent1, newCaps);
        
        vm.prank(agent1);
        registry.updateCapabilities(newCaps);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.capabilities.length, 2);
        assertEq(agent.capabilities[0], "machine-learning");
        assertEq(agent.capabilities[1], "blockchain");
    }
    
    /// @dev Unregistered agent cannot update capabilities
    function testUpdateCapabilities_unregisteredReverts() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(stranger);
        vm.expectRevert("Agent not registered");
        registry.updateCapabilities(caps);
    }
    
    /// @dev Can clear capabilities by passing empty array
    function testUpdateCapabilities_clearCapabilities() public {
        string[] memory caps = new string[](2);
        caps[0] = "data-analysis";
        caps[1] = "machine-learning";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        // Clear capabilities
        string[] memory emptyCaps = new string[](0);
        vm.prank(agent1);
        registry.updateCapabilities(emptyCaps);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.capabilities.length, 0);
    }
    
    // ═══════════════════════════════════════════════════════════════════
    // REPUTATION UPDATES (Market-only)
    // ═══════════════════════════════════════════════════════════════════
    
    /// @dev Market can update reputation on success
    function testUpdateReputation_successIncreases() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        // Market updates reputation
        vm.expectEmit(true, false, false, true);
        emit ReputationUpdated(agent1, 110, true);
        
        vm.prank(address(market));
        registry.updateReputation(agent1, true);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.reputationScore, 110, "Reputation increases by 10");
        assertEq(agent.completedTasks, 1);
        assertEq(agent.failedTasks, 0);
    }
    
    /// @dev Market can update reputation on failure
    function testUpdateReputation_failureDecreases() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        // Market updates reputation (failure)
        vm.expectEmit(true, false, false, true);
        emit ReputationUpdated(agent1, 85, false);
        
        vm.prank(address(market));
        registry.updateReputation(agent1, false);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.reputationScore, 85, "Reputation decreases by 15");
        assertEq(agent.completedTasks, 0);
        assertEq(agent.failedTasks, 1);
    }
    
    /// @dev Reputation cannot go below zero
    function testUpdateReputation_cannotGoNegative() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        // Fail multiple times to bring score below 15
        vm.startPrank(address(market));
        registry.updateReputation(agent1, false); // 100 - 15 = 85
        registry.updateReputation(agent1, false); // 85 - 15 = 70
        registry.updateReputation(agent1, false); // 70 - 15 = 55
        registry.updateReputation(agent1, false); // 55 - 15 = 40
        registry.updateReputation(agent1, false); // 40 - 15 = 25
        registry.updateReputation(agent1, false); // 25 - 15 = 10
        registry.updateReputation(agent1, false); // 10 < 15, so set to 0
        vm.stopPrank();
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.reputationScore, 0, "Reputation cannot go negative");
        assertEq(agent.failedTasks, 7);
    }
    
    /// @dev Only market can update reputation
    function testUpdateReputation_onlyMarketCanUpdate() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        // Stranger tries to update
        vm.prank(stranger);
        vm.expectRevert("Only TaskMarket can update reputation");
        registry.updateReputation(agent1, true);
        
        // Agent tries to update their own reputation
        vm.prank(agent1);
        vm.expectRevert("Only TaskMarket can update reputation");
        registry.updateReputation(agent1, true);
    }
    
    /// @dev Cannot update reputation for unregistered agent
    function testUpdateReputation_unregisteredReverts() public {
        vm.prank(address(market));
        vm.expectRevert("Agent not registered");
        registry.updateReputation(stranger, true);
    }
    
    /// @dev Multiple reputation updates accumulate correctly
    function testUpdateReputation_multipleUpdates() public {
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Agent One", caps);
        
        vm.startPrank(address(market));
        registry.updateReputation(agent1, true);  // +10 = 110
        registry.updateReputation(agent1, true);  // +10 = 120
        registry.updateReputation(agent1, false); // -15 = 105
        registry.updateReputation(agent1, true);  // +10 = 115
        vm.stopPrank();
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.reputationScore, 115);
        assertEq(agent.completedTasks, 3);
        assertEq(agent.failedTasks, 1);
    }
    
    // ═══════════════════════════════════════════════════════════════════
    // END-TO-END WITH TASKMARKET
    // ═══════════════════════════════════════════════════════════════════
    
    /// @dev End-to-end: register agent, complete task, verify reputation update
    function testEndToEnd_completeTaskUpdatesReputation() public {
        // Register agent
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Worker Agent", caps);
        
        // Set registry in market
        market.setRegistry(address(registry));
        
        // Create task
        address buyer = makeAddr("buyer");
        vm.deal(buyer, 10 ether);
        vm.deal(agent1, 10 ether);
        
        vm.prank(buyer);
        uint256 taskId = market.createTask{value: 1 ether}(
            "ipfs://spec",
            "data-analysis",
            block.timestamp + 3600
        );
        
        // Agent bids
        vm.prank(agent1);
        uint256 bidId = market.submitBid{value: 0.1 ether}(taskId, 1 ether, 60);
        
        // Select worker
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        
        // Submit result
        vm.prank(agent1);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(1)));
        
        // Verify (pass)
        uint256 initialRep = registry.getAgent(agent1).reputationScore;
        
        vm.prank(buyer);
        market.verifyResult(taskId, true);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.reputationScore, initialRep + 10, "Reputation increased");
        assertEq(agent.completedTasks, 1);
        assertEq(agent.failedTasks, 0);
    }
    
    /// @dev End-to-end: failed task decreases reputation
    function testEndToEnd_failedTaskDecreasesReputation() public {
        // Register agent
        string[] memory caps = new string[](1);
        caps[0] = "data-analysis";
        
        vm.prank(agent1);
        registry.registerAgent("Worker Agent", caps);
        
        // Set registry in market
        market.setRegistry(address(registry));
        
        // Create task
        address buyer = makeAddr("buyer");
        vm.deal(buyer, 10 ether);
        vm.deal(agent1, 10 ether);
        
        vm.prank(buyer);
        uint256 taskId = market.createTask{value: 1 ether}(
            "ipfs://spec",
            "data-analysis",
            block.timestamp + 3600
        );
        
        // Agent bids
        vm.prank(agent1);
        uint256 bidId = market.submitBid{value: 0.1 ether}(taskId, 1 ether, 60);
        
        // Select worker
        vm.prank(buyer);
        market.selectWorker(taskId, bidId);
        
        // Submit result
        vm.prank(agent1);
        market.submitResult(taskId, "ipfs://result", bytes32(uint256(1)));
        
        // Verify (fail)
        uint256 initialRep = registry.getAgent(agent1).reputationScore;
        
        vm.prank(buyer);
        market.verifyResult(taskId, false);
        
        IAgentRegistry.Agent memory agent = registry.getAgent(agent1);
        assertEq(agent.reputationScore, initialRep - 15, "Reputation decreased");
        assertEq(agent.completedTasks, 0);
        assertEq(agent.failedTasks, 1);
    }
}
