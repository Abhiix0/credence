// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// Minimal test structure mock for Foundry compatibility
import "../src/TaskMarket.sol";
import "../src/AgentRegistry.sol";

contract TaskMarketTest {
    TaskMarket market;
    AgentRegistry registry;

    address buyer = address(0x1111);
    address worker = address(0x2222);

    function setUp() public {
        market = new TaskMarket();
        registry = new AgentRegistry(address(market));
        market.setRegistry(address(registry));
    }

    function testCreateTask() public {
        uint256 deadline = block.timestamp + 3600;
        uint256 taskId = market.createTask{value: 1 ether}(
            "ipfs://task-spec-01",
            "data-analysis",
            deadline
        );

        ITaskMarket.Task memory task = market.getTask(taskId);
        require(task.id == 1, "Task ID should be 1");
        require(task.reward == 1 ether, "Reward should be 1 ether");
        require(task.status == ITaskMarket.TaskStatus.Open, "Task should be Open");
    }
}
