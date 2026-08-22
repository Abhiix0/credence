import React, { useState } from 'react';
import {
  Bot,
  Layers,
  FileCode2,
  Terminal,
  ShieldCheck,
  Zap,
  ArrowRight,
  Play,
  CheckCircle2,
  Code2,
  ExternalLink,
  Cpu,
  RefreshCw,
  FolderGit2,
  BookOpen,
  Scale,
  ShieldAlert,
  Coins
} from 'lucide-react';

// Scaffold project files content for direct inspection
const PROJECT_FILES: Record<string, { lang: string; path: string; desc: string; code: string }> = {
  'contracts/src/TaskMarket.sol': {
    lang: 'solidity',
    path: 'contracts/src/TaskMarket.sol',
    desc: 'Escrow deposit, bidding, worker assignment, and verification settlement contract.',
    code: `// SPDX-License-Identifier: MIT
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

    function createTask(
        string calldata specificationUri,
        string calldata requiredCapability,
        uint256 deadline
    ) external payable override returns (uint256) {
        require(msg.value > 0, "Reward must be greater than zero");
        require(deadline > block.timestamp, "Deadline must be in future");

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

    function submitBid(uint256 taskId, uint256 proposedPrice, uint256 estimatedDuration) external override returns (uint256) {
        Task storage task = _tasks[taskId];
        require(task.status == TaskStatus.Open, "Task not open");
        require(proposedPrice <= task.reward, "Bid exceeds reward");

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

    function verifyResult(uint256 taskId, bool passed) external override {
        Task storage task = _tasks[taskId];
        require(task.status == TaskStatus.Submitted, "Result not submitted");
        Bid memory bid = _bids[task.acceptedBidId];
        uint256 payment = bid.proposedPrice > 0 ? bid.proposedPrice : task.reward;

        if (passed) {
            task.status = TaskStatus.VerifiedPass;
            payable(task.selectedWorker).transfer(payment);
            if (address(registry) != address(0)) registry.updateReputation(task.selectedWorker, true);
            emit TaskSettled(taskId, task.selectedWorker, payment, true);
        } else {
            task.status = TaskStatus.VerifiedFail;
            payable(task.creator).transfer(task.reward);
            if (address(registry) != address(0)) registry.updateReputation(task.selectedWorker, false);
            emit TaskSettled(taskId, task.creator, task.reward, false);
        }
    }
}`
  },
  'agent-runtime/src/agents/base_agent.py': {
    lang: 'python',
    path: 'agent-runtime/src/agents/base_agent.py',
    desc: 'Core autonomous agent loop: Observe -> Discover -> Evaluate -> Decide -> Sign -> Execute -> Submit.',
    code: `import logging, time
from typing import Optional, List, Tuple
from ..models import Agent, Task, TaskStatus
from ..policies import BasePolicy, ConservativePolicy, AggressivePolicy, ReputationPolicy
from ..wallet import WalletSigner
from ..market import TaskMarketClient
from ..execution import TaskExecutor

class AutonomousAgent:
    """
    Autonomous AI Agent executing on Monad testnet.
    Loop: Observe -> Discover -> Evaluate -> Decide -> Sign Tx -> Execute -> Submit -> Repeat
    """
    def __init__(self, name: Optional[str] = None):
        self.signer = WalletSigner()
        self.market = TaskMarketClient(self.signer)
        self.executor = TaskExecutor()
        self.policy: BasePolicy = ConservativePolicy()

    def observe(self) -> None:
        """Observe wallet balance and network parameters."""
        self.balance = self.signer.get_balance()

    def discover(self) -> List[Task]:
        """Discover open tasks from Monad TaskMarket contract."""
        return self.market.fetch_open_tasks()

    def evaluate_and_decide(self, task: Task) -> Optional[dict]:
        """Evaluate task via active policy."""
        should_bid, price, duration = self.policy.evaluate(self.agent_state, task)
        if should_bid and price and duration:
            return {"task_id": task.task_id, "proposed_price": price, "estimated_duration": duration}
        return None

    def sign_and_submit_bid(self, decision: dict) -> Optional[str]:
        """Sign and broadcast bid transaction to Monad testnet."""
        return self.market.submit_bid(
            task_id=decision["task_id"],
            proposed_price=decision["proposed_price"],
            estimated_duration=decision["estimated_duration"]
        )

    def execute_task(self, task: Task) -> Tuple[str, bytes]:
        """Run task specification with Gemini AI reasoning."""
        return self.executor.execute(task)

    def submit_result(self, task_id: int, result_uri: str, result_hash: bytes) -> Optional[str]:
        """Submit cryptographic proof to Monad contract."""
        return self.market.submit_task_result(task_id, result_uri, result_hash)

    def step(self) -> None:
        self.observe()
        tasks = self.discover()
        for task in tasks:
            decision = self.evaluate_and_decide(task)
            if decision:
                self.sign_and_submit_bid(decision)`
  },
  'agent-runtime/src/models.py': {
    lang: 'python',
    path: 'agent-runtime/src/models.py',
    desc: 'Shared conceptual models: Agent, Task, Bid, Settlement, Reputation.',
    code: `from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    OPEN = "Open"
    ASSIGNED = "Assigned"
    SUBMITTED = "Submitted"
    VERIFIED_PASS = "VerifiedPass"
    VERIFIED_FAIL = "VerifiedFail"
    CANCELLED = "Cancelled"

class Reputation(BaseModel):
    agent_address: str
    score: int = 100
    completed_tasks: int = 0
    failed_tasks: int = 0
    last_updated: int = 0

class Agent(BaseModel):
    wallet_address: str
    name: str = "AutonomousAgent"
    balance_wei: int = 0
    capabilities: List[str] = Field(default_factory=list)
    reputation: Reputation
    policy_name: str = "ConservativePolicy"
    is_active: bool = True

class Task(BaseModel):
    task_id: int
    creator: str
    specification_uri: str
    required_capability: str
    reward_wei: int
    deadline: int
    status: TaskStatus = TaskStatus.OPEN
    selected_worker: Optional[str] = None
    accepted_bid_id: Optional[int] = None
    result_uri: Optional[str] = None
    result_hash: Optional[str] = None

class Bid(BaseModel):
    bid_id: int
    task_id: int
    bidder: str
    proposed_price_wei: int
    estimated_duration_sec: int
    timestamp: int
    is_accepted: bool = False

class Settlement(BaseModel):
    settlement_id: str
    task_id: int
    recipient: str
    amount_wei: int
    timestamp: int
    result_proof: str
    passed: bool`
  },
  'frontend/lib/viemClient.ts': {
    lang: 'typescript',
    path: 'frontend/lib/viemClient.ts',
    desc: 'Viem client configured for Monad testnet (Chain ID 10143).',
    code: `import { createPublicClient, defineChain, http } from 'viem';

export const monadTestnet = defineChain({
  id: 10143,
  name: 'Monad Testnet',
  nativeCurrency: {
    name: 'Monad',
    symbol: 'MON',
    decimals: 18,
  },
  rpcUrls: {
    default: { http: [process.env.NEXT_PUBLIC_MONAD_RPC_URL || 'https://testnet-rpc.monad.xyz'] },
  },
  blockExplorers: {
    default: { name: 'MonadExplorer', url: 'https://testnet.monadexplorer.com' },
  },
  testnet: true,
});

export const publicClient = createPublicClient({
  chain: monadTestnet,
  transport: http(),
});`
  },
  'docs/architecture.md': {
    lang: 'markdown',
    path: 'docs/architecture.md',
    desc: 'System architecture, conceptual domain models, and lifecycle diagram.',
    code: `# Architecture Specification

## Overview
The Autonomous Agent Economy is a decentralized protocol built on Monad testnet that allows sovereign software agents to participate in open labor and computational markets.

## Core System Flow
Agent needs work 
-> task created 
-> workers discover task 
-> workers submit bids 
-> buyer selects worker 
-> payment enters escrow 
-> worker executes 
-> verifier checks result 
-> pass/fail 
-> settlement 
-> reputation update 
-> agent repeats

## Core Agent Loop
Observe -> Discover -> Evaluate -> Decide -> Sign transaction -> Execute -> Submit result -> Repeat`
  }
};

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'flow' | 'policies' | 'files' | 'simulator'>('overview');
  const [selectedFile, setSelectedFile] = useState<string>('contracts/src/TaskMarket.sol');
  
  // Simulator State
  const [simStep, setSimStep] = useState<number>(0);
  const [simPolicy, setSimPolicy] = useState<'ConservativePolicy' | 'AggressivePolicy' | 'ReputationPolicy'>('ConservativePolicy');
  const [simReputation, setSimReputation] = useState<number>(100);
  const [simBalance, setSimBalance] = useState<number>(1.25);

  const steps = [
    { title: '1. Task Created', desc: 'Buyer posts task: "Market Sentiment Digest" with 0.10 MON escrow reward.' },
    { title: '2. Agent Observe & Discover', desc: 'Worker agent polls Monad RPC and discovers matching "data-analysis" task.' },
    { title: '3. Policy Evaluation', desc: `Agent applies ${simPolicy}: Evaluates reward margin and sets bid.` },
    { title: '4. Sign & Submit Bid', desc: 'Agent signs transaction on Monad testnet submitting proposed price.' },
    { title: '5. Worker Selected', desc: 'Buyer accepts bid. Contract locks escrow funds and assigns worker address.' },
    { title: '6. AI Task Execution', desc: 'Agent processes input specification using Gemini AI reasoning.' },
    { title: '7. Submit Proof', desc: 'Agent uploads result proof (hash: 0x8f3c...e412) to Monad TaskMarket.' },
    { title: '8. Verification & Settlement', desc: 'Verifier validates result: 0.095 MON released to worker, reputation +10.' }
  ];

  const handleNextSimStep = () => {
    if (simStep < steps.length - 1) {
      setSimStep(simStep + 1);
      if (simStep === 6) {
        setSimReputation((prev) => prev + 10);
        setSimBalance((prev) => parseFloat((prev + 0.095).toFixed(4)));
      }
    } else {
      setSimStep(0);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 font-sans flex flex-col selection:bg-zinc-200">
      {/* Top Banner / Header */}
      <header className="bg-white border-b border-zinc-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-zinc-900 flex items-center justify-center text-white shadow-xs">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-base font-bold text-zinc-900 tracking-tight">
                  Autonomous Agent Economy
                </h1>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-violet-100 text-violet-800 border border-violet-200">
                  Monad Testnet
                </span>
              </div>
              <p className="text-xs text-zinc-500 font-mono">Monorepo Project Scaffold</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="hidden sm:inline-flex items-center px-2.5 py-1 rounded-md bg-emerald-50 border border-emerald-200 text-xs font-mono text-emerald-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse" />
              Chain ID: 10143
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 border-t border-zinc-100 overflow-x-auto">
          {[
            { id: 'overview', label: 'Architecture & Spec', icon: Layers },
            { id: 'flow', label: 'Core Economic Flow', icon: Zap },
            { id: 'policies', label: 'Agent Policies', icon: Scale },
            { id: 'files', label: 'Monorepo Codebase', icon: FolderGit2 },
            { id: 'simulator', label: 'Loop Simulator', icon: Play },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-3 px-4 text-xs font-medium border-b-2 transition whitespace-nowrap ${
                  isActive
                    ? 'border-zinc-900 text-zinc-900 bg-zinc-50/50'
                    : 'border-transparent text-zinc-500 hover:text-zinc-700 hover:border-zinc-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Hero Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-3">
                <div className="w-9 h-9 rounded-lg bg-zinc-100 flex items-center justify-center text-zinc-900">
                  <Code2 className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-zinc-900">Smart Contracts</h3>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  Solidity + Foundry on Monad testnet. Non-custodial task escrow, worker assignment, and reputation ledger.
                </p>
                <div className="pt-2 text-xs font-mono text-zinc-400">contracts/src/TaskMarket.sol</div>
              </div>

              <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-3">
                <div className="w-9 h-9 rounded-lg bg-zinc-100 flex items-center justify-center text-zinc-900">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-zinc-900">Agent Runtime</h3>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  Python daemon using web3.py. Autonomous Observe-Decide-Execute loop with pluggable bidding policies and Gemini AI reasoning.
                </p>
                <div className="pt-2 text-xs font-mono text-zinc-400">agent-runtime/src/agents/base_agent.py</div>
              </div>

              <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-3">
                <div className="w-9 h-9 rounded-lg bg-zinc-100 flex items-center justify-center text-zinc-900">
                  <Layers className="w-5 h-5" />
                </div>
                <h3 className="text-base font-bold text-zinc-900">Frontend App</h3>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  Next.js App Router + TypeScript + Tailwind + Viem. Real-time task board, agent registry profiles, and settlement trackers.
                </p>
                <div className="pt-2 text-xs font-mono text-zinc-400">frontend/app/page.tsx</div>
              </div>
            </div>

            {/* Conceptual Domain Models Section */}
            <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-6">
              <div>
                <h3 className="text-base font-bold text-zinc-900">Shared Conceptual Models</h3>
                <p className="text-xs text-zinc-500 mt-1">
                  Unified data contracts defined across Solidity, Python, and TypeScript layers.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                {[
                  {
                    name: 'Agent',
                    fields: ['wallet: address', 'balance: uint256', 'capabilities: string[]', 'reputationScore: uint256', 'policy: string'],
                    desc: 'Sovereign actor with keypair and decision policy.'
                  },
                  {
                    name: 'Task',
                    fields: ['id: uint256', 'creator: address', 'specUri: string', 'reward: uint256', 'status: TaskStatus'],
                    desc: 'Unit of computational work with escrowed funds.'
                  },
                  {
                    name: 'Bid',
                    fields: ['id: uint256', 'taskId: uint256', 'bidder: address', 'proposedPrice: uint256', 'durationSec: uint256'],
                    desc: 'Offer submitted by agent to execute work.'
                  },
                  {
                    name: 'Settlement',
                    fields: ['taskId: uint256', 'recipient: address', 'amount: uint256', 'resultProof: string', 'passed: bool'],
                    desc: 'Economic resolution and escrow release.'
                  },
                  {
                    name: 'Reputation',
                    fields: ['score: uint256', 'completedTasks: uint256', 'failedTasks: uint256', 'lastUpdated: uint256'],
                    desc: 'Cumulative trust index and track record.'
                  }
                ].map((model) => (
                  <div key={model.name} className="p-4 rounded-xl bg-zinc-50 border border-zinc-200 space-y-2">
                    <div className="text-xs font-bold text-zinc-900 font-mono">{model.name}</div>
                    <p className="text-[11px] text-zinc-500 leading-tight">{model.desc}</p>
                    <div className="pt-2 border-t border-zinc-200 space-y-1 font-mono text-[10px] text-zinc-600">
                      {model.fields.map((f, i) => (
                        <div key={i} className="truncate">{f}</div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quickstart Command Bar */}
            <div className="p-6 rounded-2xl bg-zinc-900 text-white shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Terminal className="w-5 h-5 text-emerald-400" />
                  <h3 className="text-sm font-bold tracking-tight">Quickstart Commands</h3>
                </div>
                <span className="text-xs text-zinc-400 font-mono">./scripts/setup.sh</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs text-zinc-300">
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <div className="text-[10px] text-zinc-500 mb-1"># 1. Setup All Modules</div>
                  <code>./scripts/setup.sh</code>
                </div>
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <div className="text-[10px] text-zinc-500 mb-1"># 2. Deploy to Monad</div>
                  <code>./scripts/deploy_contracts.sh</code>
                </div>
                <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                  <div className="text-[10px] text-zinc-500 mb-1"># 3. Launch Agent Loop</div>
                  <code>./scripts/run_agent.sh ConservativePolicy</code>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Flow */}
        {activeTab === 'flow' && (
          <div className="space-y-8">
            <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-6">
              <div>
                <h3 className="text-base font-bold text-zinc-900">Core Economic Flow</h3>
                <p className="text-xs text-zinc-500 mt-0.5">
                  End-to-end decentralized coordination between buyers, autonomous worker agents, and Monad smart contracts.
                </p>
              </div>

              <div className="relative pl-6 space-y-6 border-l-2 border-zinc-200">
                {[
                  { step: '1', title: 'Agent needs work / Task created', desc: 'Buyer creates task on TaskMarket and deposits escrow reward in MON.' },
                  { step: '2', title: 'Workers discover task', desc: 'Agents poll Monad testnet RPC for TaskCreated event logs.' },
                  { step: '3', title: 'Workers submit bids', desc: 'Agents run evaluation policies against task spec and submit on-chain bids.' },
                  { step: '4', title: 'Buyer selects worker', desc: 'Buyer selects optimal bid; contract transitions state to Assigned.' },
                  { step: '5', title: 'Payment enters escrow', desc: 'Funds remain locked in non-custodial smart contract.' },
                  { step: '6', title: 'Worker executes', desc: 'Selected agent runs task payload, invoking Gemini AI reasoning where required.' },
                  { step: '7', title: 'Verifier checks result', desc: 'Result cryptographic proof is posted on-chain and verified.' },
                  { step: '8', title: 'Pass / Fail Settlement', desc: 'Pass: escrow released to worker. Fail: funds refunded to buyer.' },
                  { step: '9', title: 'Reputation update', desc: 'Worker reputation score increments (+10 on pass, -15 on fail).' },
                  { step: '10', title: 'Agent repeats', desc: 'Agent updates local state and loops back to discovery.' }
                ].map((item, idx) => (
                  <div key={idx} className="relative">
                    <div className="absolute -left-[31px] top-0 w-6 h-6 rounded-full bg-zinc-900 text-white text-[11px] font-bold flex items-center justify-center">
                      {item.step}
                    </div>
                    <h4 className="text-sm font-semibold text-zinc-900">{item.title}</h4>
                    <p className="text-xs text-zinc-500 mt-0.5">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Core Agent Internal Loop */}
            <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-4">
              <h3 className="text-base font-bold text-zinc-900">Core Agent Lifecycle Loop</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2 text-center text-xs font-mono">
                {['Observe', 'Discover', 'Evaluate', 'Decide', 'Sign Tx', 'Execute', 'Submit', 'Repeat'].map((stage, i) => (
                  <div key={stage} className="p-3 rounded-xl bg-zinc-50 border border-zinc-200 flex flex-col items-center justify-center">
                    <span className="text-[10px] text-zinc-400 mb-1">Stage {i + 1}</span>
                    <span className="font-bold text-zinc-800">{stage}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Policies */}
        {activeTab === 'policies' && (
          <div className="space-y-6">
            <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-2">
              <h3 className="text-base font-bold text-zinc-900">Pluggable Bidding Policies</h3>
              <p className="text-xs text-zinc-500">
                Autonomous agents evaluate market conditions and calculate pricing bids using swappable policy modules.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Conservative */}
              <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-base font-bold text-zinc-900">ConservativePolicy</h4>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-50 text-blue-700 border border-blue-200">
                    High Margin
                  </span>
                </div>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  Strictly validates capability match. Bids at 95% of maximum task reward to ensure profitability. Requires generous execution duration buffer (1800s).
                </p>
                <div className="p-3 bg-zinc-50 rounded-xl space-y-1.5 text-xs font-mono">
                  <div className="flex justify-between text-zinc-600">
                    <span>Reward Ratio:</span>
                    <span className="font-bold text-zinc-900">95%</span>
                  </div>
                  <div className="flex justify-between text-zinc-600">
                    <span>Duration Buffer:</span>
                    <span className="font-bold text-zinc-900">1800 sec</span>
                  </div>
                  <div className="flex justify-between text-zinc-600">
                    <span>Capability Check:</span>
                    <span className="font-bold text-emerald-600">Strict</span>
                  </div>
                </div>
              </div>

              {/* Aggressive */}
              <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-base font-bold text-zinc-900">AggressivePolicy</h4>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-50 text-amber-700 border border-amber-200">
                    Volume Leader
                  </span>
                </div>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  Bids aggressively at 75% of maximum reward to undercut market competitors. Promises accelerated execution (600s).
                </p>
                <div className="p-3 bg-zinc-50 rounded-xl space-y-1.5 text-xs font-mono">
                  <div className="flex justify-between text-zinc-600">
                    <span>Reward Ratio:</span>
                    <span className="font-bold text-zinc-900">75%</span>
                  </div>
                  <div className="flex justify-between text-zinc-600">
                    <span>Duration Buffer:</span>
                    <span className="font-bold text-zinc-900">600 sec</span>
                  </div>
                  <div className="flex justify-between text-zinc-600">
                    <span>Capability Check:</span>
                    <span className="font-bold text-blue-600">Broad</span>
                  </div>
                </div>
              </div>

              {/* Reputation */}
              <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-base font-bold text-zinc-900">ReputationPolicy</h4>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-50 text-purple-700 border border-purple-200">
                    Trust-Scaled
                  </span>
                </div>
                <p className="text-xs text-zinc-500 leading-relaxed">
                  Dynamically scales bid pricing based on current on-chain reputation score. Protects track record with safe 1200s turnarounds.
                </p>
                <div className="p-3 bg-zinc-50 rounded-xl space-y-1.5 text-xs font-mono">
                  <div className="flex justify-between text-zinc-600">
                    <span>Reward Ratio:</span>
                    <span className="font-bold text-zinc-900">80% - 90%</span>
                  </div>
                  <div className="flex justify-between text-zinc-600">
                    <span>Duration Buffer:</span>
                    <span className="font-bold text-zinc-900">1200 sec</span>
                  </div>
                  <div className="flex justify-between text-zinc-600">
                    <span>Dynamic Scaling:</span>
                    <span className="font-bold text-purple-600">Score &gt; 50</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Codebase Explorer */}
        {activeTab === 'files' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* File List */}
            <div className="p-4 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-500 px-2 mb-3">
                Monorepo Files
              </h3>
              <div className="space-y-1">
                {Object.keys(PROJECT_FILES).map((key) => {
                  const file = PROJECT_FILES[key];
                  const isSelected = selectedFile === key;
                  return (
                    <button
                      key={key}
                      onClick={() => setSelectedFile(key)}
                      className={`w-full text-left p-2.5 rounded-lg text-xs font-mono transition flex items-start space-x-2 ${
                        isSelected
                          ? 'bg-zinc-900 text-white font-semibold'
                          : 'text-zinc-700 hover:bg-zinc-100'
                      }`}
                    >
                      <FileCode2 className="w-4 h-4 mt-0.5 shrink-0" />
                      <div className="truncate">
                        <div className="truncate">{key}</div>
                        <div className={`text-[10px] mt-0.5 truncate ${isSelected ? 'text-zinc-300' : 'text-zinc-400'}`}>
                          {file.desc}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Code Display */}
            <div className="lg:col-span-2 rounded-2xl bg-zinc-900 text-zinc-100 p-5 shadow-xs flex flex-col font-mono text-xs overflow-hidden border border-zinc-800">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3 mb-4">
                <div className="flex items-center space-x-2 text-zinc-300">
                  <span className="w-2.5 h-2.5 rounded-full bg-zinc-700" />
                  <span className="font-semibold">{PROJECT_FILES[selectedFile]?.path}</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 uppercase">
                  {PROJECT_FILES[selectedFile]?.lang}
                </span>
              </div>
              <pre className="overflow-x-auto flex-1 text-zinc-300 leading-relaxed font-mono p-2">
                <code>{PROJECT_FILES[selectedFile]?.code}</code>
              </pre>
            </div>
          </div>
        )}

        {/* Tab 5: Interactive Simulator */}
        {activeTab === 'simulator' && (
          <div className="p-6 rounded-2xl bg-white border border-zinc-200 shadow-xs space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-zinc-900">Autonomous Cycle Simulator</h3>
                <p className="text-xs text-zinc-500">
                  Step through the agent decision, bidding, escrow lock, execution, and settlement flow.
                </p>
              </div>

              {/* Agent Status Bar */}
              <div className="flex items-center space-x-3 bg-zinc-50 border border-zinc-200 p-2 rounded-xl text-xs font-mono">
                <div className="px-2">
                  <span className="text-zinc-400">Balance:</span> <span className="font-bold text-zinc-900">{simBalance} MON</span>
                </div>
                <div className="px-2 border-l border-zinc-200">
                  <span className="text-zinc-400">Reputation:</span> <span className="font-bold text-amber-600">{simReputation}</span>
                </div>
              </div>
            </div>

            {/* Policy Selector for Simulator */}
            <div className="flex items-center space-x-3 text-xs">
              <span className="text-zinc-500 font-medium">Select Active Policy:</span>
              {(['ConservativePolicy', 'AggressivePolicy', 'ReputationPolicy'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setSimPolicy(p)}
                  className={`px-3 py-1.5 rounded-lg border font-mono transition ${
                    simPolicy === p
                      ? 'bg-zinc-900 text-white border-zinc-900'
                      : 'bg-white text-zinc-700 border-zinc-200 hover:bg-zinc-50'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>

            {/* Step Visualizer */}
            <div className="p-6 rounded-xl bg-zinc-50 border border-zinc-200 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-zinc-400">
                  Step {simStep + 1} of {steps.length}
                </span>
                <span className="text-xs font-mono font-medium text-violet-700 bg-violet-50 px-2.5 py-0.5 rounded-md border border-violet-200">
                  {simPolicy} Active
                </span>
              </div>

              <div className="space-y-1">
                <h4 className="text-lg font-bold text-zinc-900">{steps[simStep].title}</h4>
                <p className="text-sm text-zinc-600">{steps[simStep].desc}</p>
              </div>

              <div className="pt-4 flex items-center justify-between border-t border-zinc-200">
                <button
                  onClick={() => setSimStep(0)}
                  className="text-xs text-zinc-500 hover:text-zinc-900 font-mono"
                >
                  Reset Simulator
                </button>

                <button
                  onClick={handleNextSimStep}
                  className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-zinc-900 text-white text-xs font-medium hover:bg-zinc-800 transition"
                >
                  <span>{simStep === steps.length - 1 ? 'Restart Cycle' : 'Advance Next Step'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
