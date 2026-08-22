export const AgentRegistryABI = [
  {
    "type": "constructor",
    "inputs": [
      { "name": "_market", "type": "address", "internalType": "address" }
    ],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "market",
    "inputs": [],
    "outputs": [{ "name": "", "type": "address", "internalType": "address" }],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "registerAgent",
    "inputs": [
      { "name": "name", "type": "string", "internalType": "string" },
      { "name": "capabilities", "type": "string[]", "internalType": "string[]" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "updateCapabilities",
    "inputs": [
      { "name": "capabilities", "type": "string[]", "internalType": "string[]" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "updateReputation",
    "inputs": [
      { "name": "agent", "type": "address", "internalType": "address" },
      { "name": "success", "type": "bool", "internalType": "bool" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "getAgent",
    "inputs": [
      { "name": "agent", "type": "address", "internalType": "address" }
    ],
    "outputs": [
      {
        "name": "",
        "type": "tuple",
        "internalType": "struct IAgentRegistry.Agent",
        "components": [
          { "name": "wallet", "type": "address", "internalType": "address" },
          { "name": "name", "type": "string", "internalType": "string" },
          { "name": "capabilities", "type": "string[]", "internalType": "string[]" },
          { "name": "reputationScore", "type": "uint256", "internalType": "uint256" },
          { "name": "completedTasks", "type": "uint256", "internalType": "uint256" },
          { "name": "failedTasks", "type": "uint256", "internalType": "uint256" },
          { "name": "isRegistered", "type": "bool", "internalType": "bool" }
        ]
      }
    ],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "isRegisteredAgent",
    "inputs": [
      { "name": "agent", "type": "address", "internalType": "address" }
    ],
    "outputs": [{ "name": "", "type": "bool", "internalType": "bool" }],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "getAllAgents",
    "inputs": [],
    "outputs": [{ "name": "", "type": "address[]", "internalType": "address[]" }],
    "stateMutability": "view"
  },
  {
    "type": "event",
    "name": "AgentRegistered",
    "inputs": [
      { "name": "wallet", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "name", "type": "string", "indexed": false, "internalType": "string" },
      { "name": "capabilities", "type": "string[]", "indexed": false, "internalType": "string[]" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "CapabilitiesUpdated",
    "inputs": [
      { "name": "wallet", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "capabilities", "type": "string[]", "indexed": false, "internalType": "string[]" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "ReputationUpdated",
    "inputs": [
      { "name": "wallet", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "newScore", "type": "uint256", "indexed": false, "internalType": "uint256" },
      { "name": "success", "type": "bool", "indexed": false, "internalType": "bool" }
    ],
    "anonymous": false
  }
] as const;
