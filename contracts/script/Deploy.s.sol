// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../src/TaskMarket.sol";
import "../src/AgentRegistry.sol";

contract DeployScript {
    function run() external returns (address marketAddress, address registryAddress) {
        // Deploy TaskMarket
        TaskMarket market = new TaskMarket();
        
        // Deploy AgentRegistry with market address
        AgentRegistry registry = new AgentRegistry(address(market));
        
        // Link registry in TaskMarket
        market.setRegistry(address(registry));

        marketAddress = address(market);
        registryAddress = address(registry);
    }
}
