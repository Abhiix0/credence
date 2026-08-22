export const TaskMarketABI = [
  {
    "type": "constructor",
    "inputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "owner",
    "inputs": [],
    "outputs": [{ "name": "", "type": "address", "internalType": "address" }],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "registry",
    "inputs": [],
    "outputs": [{ "name": "", "type": "address", "internalType": "contract IAgentRegistry" }],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "setRegistry",
    "inputs": [
      { "name": "_registry", "type": "address", "internalType": "address" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "createTask",
    "inputs": [
      { "name": "specificationUri", "type": "string", "internalType": "string" },
      { "name": "requiredCapability", "type": "string", "internalType": "string" },
      { "name": "deadline", "type": "uint256", "internalType": "uint256" }
    ],
    "outputs": [{ "name": "", "type": "uint256", "internalType": "uint256" }],
    "stateMutability": "payable"
  },
  {
    "type": "function",
    "name": "submitBid",
    "inputs": [
      { "name": "taskId", "type": "uint256", "internalType": "uint256" },
      { "name": "proposedPrice", "type": "uint256", "internalType": "uint256" },
      { "name": "estimatedDuration", "type": "uint256", "internalType": "uint256" }
    ],
    "outputs": [{ "name": "", "type": "uint256", "internalType": "uint256" }],
    "stateMutability": "payable"
  },
  {
    "type": "function",
    "name": "selectWorker",
    "inputs": [
      { "name": "taskId", "type": "uint256", "internalType": "uint256" },
      { "name": "bidId", "type": "uint256", "internalType": "uint256" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "submitResult",
    "inputs": [
      { "name": "taskId", "type": "uint256", "internalType": "uint256" },
      { "name": "resultUri", "type": "string", "internalType": "string" },
      { "name": "resultHash", "type": "bytes32", "internalType": "bytes32" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "verifyResult",
    "inputs": [
      { "name": "taskId", "type": "uint256", "internalType": "uint256" },
      { "name": "passed", "type": "bool", "internalType": "bool" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "cancelTask",
    "inputs": [
      { "name": "taskId", "type": "uint256", "internalType": "uint256" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "expireTask",
    "inputs": [
      { "name": "taskId", "type": "uint256", "internalType": "uint256" }
    ],
    "outputs": [],
    "stateMutability": "nonpayable"
  },
  {
    "type": "function",
    "name": "getTask",
    "inputs": [
      { "name": "taskId", "type": "uint256", "internalType": "uint256" }
    ],
    "outputs": [
      {
        "name": "",
        "type": "tuple",
        "internalType": "struct ITaskMarket.Task",
        "components": [
          { "name": "id", "type": "uint256", "internalType": "uint256" },
          { "name": "creator", "type": "address", "internalType": "address" },
          { "name": "specificationUri", "type": "string", "internalType": "string" },
          { "name": "requiredCapability", "type": "string", "internalType": "string" },
          { "name": "reward", "type": "uint256", "internalType": "uint256" },
          { "name": "deadline", "type": "uint256", "internalType": "uint256" },
          { "name": "status", "type": "uint8", "internalType": "enum ITaskMarket.TaskStatus" },
          { "name": "selectedWorker", "type": "address", "internalType": "address" },
          { "name": "acceptedBidId", "type": "uint256", "internalType": "uint256" },
          { "name": "resultUri", "type": "string", "internalType": "string" },
          { "name": "resultHash", "type": "bytes32", "internalType": "bytes32" }
        ]
      }
    ],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "getBid",
    "inputs": [
      { "name": "bidId", "type": "uint256", "internalType": "uint256" }
    ],
    "outputs": [
      {
        "name": "",
        "type": "tuple",
        "internalType": "struct ITaskMarket.Bid",
        "components": [
          { "name": "id", "type": "uint256", "internalType": "uint256" },
          { "name": "taskId", "type": "uint256", "internalType": "uint256" },
          { "name": "bidder", "type": "address", "internalType": "address" },
          { "name": "proposedPrice", "type": "uint256", "internalType": "uint256" },
          { "name": "estimatedDuration", "type": "uint256", "internalType": "uint256" },
          { "name": "timestamp", "type": "uint256", "internalType": "uint256" },
          { "name": "isAccepted", "type": "bool", "internalType": "bool" },
          { "name": "stake", "type": "uint256", "internalType": "uint256" }
        ]
      }
    ],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "getTaskBids",
    "inputs": [
      { "name": "taskId", "type": "uint256", "internalType": "uint256" }
    ],
    "outputs": [{ "name": "", "type": "uint256[]", "internalType": "uint256[]" }],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "totalTasks",
    "inputs": [],
    "outputs": [{ "name": "", "type": "uint256", "internalType": "uint256" }],
    "stateMutability": "view"
  },
  {
    "type": "event",
    "name": "TaskCreated",
    "inputs": [
      { "name": "taskId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "creator", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "reward", "type": "uint256", "indexed": false, "internalType": "uint256" },
      { "name": "requiredCapability", "type": "string", "indexed": false, "internalType": "string" },
      { "name": "deadline", "type": "uint256", "indexed": false, "internalType": "uint256" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "BidSubmitted",
    "inputs": [
      { "name": "bidId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "taskId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "bidder", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "proposedPrice", "type": "uint256", "indexed": false, "internalType": "uint256" },
      { "name": "estimatedDuration", "type": "uint256", "indexed": false, "internalType": "uint256" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "WorkerSelected",
    "inputs": [
      { "name": "taskId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "bidId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "worker", "type": "address", "indexed": true, "internalType": "address" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "ResultSubmitted",
    "inputs": [
      { "name": "taskId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "worker", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "resultUri", "type": "string", "indexed": false, "internalType": "string" },
      { "name": "resultHash", "type": "bytes32", "indexed": false, "internalType": "bytes32" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "TaskSettled",
    "inputs": [
      { "name": "taskId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "recipient", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "amount", "type": "uint256", "indexed": false, "internalType": "uint256" },
      { "name": "passed", "type": "bool", "indexed": false, "internalType": "bool" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "TaskCancelled",
    "inputs": [
      { "name": "taskId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "creator", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "refundAmount", "type": "uint256", "indexed": false, "internalType": "uint256" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "StakeSlashed",
    "inputs": [
      { "name": "taskId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "bidId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "worker", "type": "address", "indexed": true, "internalType": "address" },
      { "name": "amount", "type": "uint256", "indexed": false, "internalType": "uint256" }
    ],
    "anonymous": false
  },
  {
    "type": "event",
    "name": "TaskExpired",
    "inputs": [
      { "name": "taskId", "type": "uint256", "indexed": true, "internalType": "uint256" },
      { "name": "creatorRefund", "type": "uint256", "indexed": false, "internalType": "uint256" },
      { "name": "totalStakesRefunded", "type": "uint256", "indexed": false, "internalType": "uint256" }
    ],
    "anonymous": false
  }
] as const;

export enum TaskStatus {
  Open = 0,
  Assigned = 1,
  Submitted = 2,
  VerifiedPass = 3,
  VerifiedFail = 4,
  Cancelled = 5,
  Expired = 6
}
