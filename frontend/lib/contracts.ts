export const TASK_MARKET_ADDRESS = (process.env.NEXT_PUBLIC_TASK_MARKET_ADDRESS ||
  '0x0000000000000000000000000000000000000000') as `0x${string}`;

export const AGENT_REGISTRY_ADDRESS = (process.env.NEXT_PUBLIC_AGENT_REGISTRY_ADDRESS ||
  '0x0000000000000000000000000000000000000000') as `0x${string}`;

export const TASK_MARKET_ABI = [
  {
    inputs: [{ internalType: 'uint256', name: 'taskId', type: 'uint256' }],
    name: 'getTask',
    outputs: [
      {
        components: [
          { internalType: 'uint256', name: 'id', type: 'uint256' },
          { internalType: 'address', name: 'creator', type: 'address' },
          { internalType: 'string', name: 'specificationUri', type: 'string' },
          { internalType: 'string', name: 'requiredCapability', type: 'string' },
          { internalType: 'uint256', name: 'reward', type: 'uint256' },
          { internalType: 'uint256', name: 'deadline', type: 'uint256' },
          { internalType: 'uint8', name: 'status', type: 'uint8' },
          { internalType: 'address', name: 'selectedWorker', type: 'address' },
          { internalType: 'uint256', name: 'acceptedBidId', type: 'uint256' },
          { internalType: 'string', name: 'resultUri', type: 'string' },
          { internalType: 'bytes32', name: 'resultHash', type: 'bytes32' },
        ],
        internalType: 'struct ITaskMarket.Task',
        name: '',
        type: 'tuple',
      },
    ],
    stateMutability: 'view',
    type: 'function',
  },
  {
    inputs: [],
    name: 'totalTasks',
    outputs: [{ internalType: 'uint256', name: '', type: 'uint256' }],
    stateMutability: 'view',
    type: 'function',
  },
  {
    inputs: [
      { internalType: 'string', name: 'specificationUri', type: 'string' },
      { internalType: 'string', name: 'requiredCapability', type: 'string' },
      { internalType: 'uint256', name: 'deadline', type: 'uint256' },
    ],
    name: 'createTask',
    outputs: [{ internalType: 'uint256', name: '', type: 'uint256' }],
    stateMutability: 'payable',
    type: 'function',
  },
] as const;

export const AGENT_REGISTRY_ABI = [
  {
    inputs: [{ internalType: 'address', name: 'agent', type: 'address' }],
    name: 'getAgent',
    outputs: [
      {
        components: [
          { internalType: 'address', name: 'wallet', type: 'address' },
          { internalType: 'string', name: 'name', type: 'string' },
          { internalType: 'string[]', name: 'capabilities', type: 'string[]' },
          { internalType: 'uint256', name: 'reputationScore', type: 'uint256' },
          { internalType: 'uint256', name: 'completedTasks', type: 'uint256' },
          { internalType: 'uint256', name: 'failedTasks', type: 'uint256' },
          { internalType: 'bool', name: 'isRegistered', type: 'bool' },
        ],
        internalType: 'struct IAgentRegistry.Agent',
        name: '',
        type: 'tuple',
      },
    ],
    stateMutability: 'view',
    type: 'function',
  },
] as const;
