"""
Full Economy Runner - Start all agents concurrently.

This script loads agent configurations from environment variables and runs
a complete autonomous agent economy with buyers, workers, bad workers, and verifiers.

Environment Variables Format:
    AGENT_1_NAME=BuyerBot
    AGENT_1_PRIVATE_KEY=0x...
    AGENT_1_ROLE=buyer
    AGENT_1_POLICY=ConservativePolicy
    AGENT_1_RISK_TOLERANCE=50.0
    
    AGENT_2_NAME=WorkerBot1
    AGENT_2_PRIVATE_KEY=0x...
    AGENT_2_ROLE=worker
    AGENT_2_POLICY=AggressivePolicy
    AGENT_2_CAPABILITIES=text-processing,data-analysis
    
    AGENT_3_NAME=BadWorkerBot
    AGENT_3_PRIVATE_KEY=0x...
    AGENT_3_ROLE=bad_worker
    AGENT_3_CAPABILITIES=text-processing
    
    AGENT_4_NAME=VerifierBot
    AGENT_4_PRIVATE_KEY=0x...
    AGENT_4_ROLE=verifier

Usage:
    python run_economy.py [--interval SECONDS]
    
    --interval: Polling interval in seconds (default: 15)
"""

import argparse
import logging
import sys
import threading
import time
from typing import List, Optional

from src.config import load_agent_configs_from_env, AgentConfig
from src.agents.buyer_agent import BuyerAgent
from src.agents.base_agent import AutonomousAgent
from src.agents.bad_worker_agent import BadWorkerAgent
from src.agents.verifier_agent import VerifierAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("EconomyRunner")


class AgentRunner:
    """Manages execution of a single agent in a background thread."""
    
    def __init__(self, agent, config: AgentConfig, interval_seconds: int):
        self.agent = agent
        self.config = config
        self.interval_seconds = interval_seconds
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.error_count = 0
        self.max_errors = 10
    
    def start(self) -> None:
        """Start the agent in a background thread."""
        if self.running:
            logger.warning(f"Agent {self.config.name} is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(
            target=self._run_loop,
            name=f"Agent-{self.config.name}",
            daemon=True
        )
        self.thread.start()
        logger.info(f"✓ Started {self.config.name} ({self.config.role})")
    
    def stop(self) -> None:
        """Stop the agent."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
        logger.info(f"✓ Stopped {self.config.name}")
    
    def _run_loop(self) -> None:
        """Agent execution loop with error handling."""
        logger.info(f"[{self.config.name}] Starting agent loop (interval: {self.interval_seconds}s)")
        
        while self.running:
            try:
                # Execute one agent cycle
                self.agent.step()
                
                # Reset error count on success
                self.error_count = 0
                
            except KeyboardInterrupt:
                logger.info(f"[{self.config.name}] Interrupted by user")
                self.running = False
                break
                
            except Exception as e:
                self.error_count += 1
                logger.error(
                    f"[{self.config.name}] Error in agent cycle ({self.error_count}/{self.max_errors}): {e}",
                    exc_info=True
                )
                
                # Stop agent if too many errors
                if self.error_count >= self.max_errors:
                    logger.error(
                        f"[{self.config.name}] Too many errors ({self.max_errors}), stopping agent"
                    )
                    self.running = False
                    break
            
            # Wait before next cycle
            if self.running:
                time.sleep(self.interval_seconds)
        
        logger.info(f"[{self.config.name}] Agent loop terminated")


class EconomyRunner:
    """Manages the full multi-agent economy."""
    
    def __init__(self, interval_seconds: int = 15):
        self.interval_seconds = interval_seconds
        self.runners: List[AgentRunner] = []
    
    def instantiate_agent(self, config: AgentConfig):
        """
        Instantiate the appropriate agent class based on role.
        
        Args:
            config: Agent configuration
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If role is invalid or required fields are missing
        """
        role = config.role.lower()
        
        # Validate required fields
        if not config.private_key:
            raise ValueError(f"Agent {config.name} missing private_key")
        
        # Set private key in environment for agent to use
        # (Agents expect AGENT_PRIVATE_KEY or role-specific key)
        import os
        
        if role == "buyer":
            os.environ["BUYER_PRIVATE_KEY"] = config.private_key
            os.environ["BUYER_NAME"] = config.name
            os.environ["BUYER_POLICY"] = config.policy_name
            os.environ["BUYER_RISK_TOLERANCE"] = str(config.risk_tolerance * 100)  # Convert 0-1 to 0-100
            
            logger.info(f"Instantiating BuyerAgent: {config.name}")
            return BuyerAgent(
                name=config.name,
                policy_name=config.policy_name,
                risk_tolerance=config.risk_tolerance * 100  # Convert 0-1 to 0-100
            )
        
        elif role == "worker":
            os.environ["AGENT_PRIVATE_KEY"] = config.private_key
            os.environ["AGENT_NAME"] = config.name
            os.environ["AGENT_POLICY"] = config.policy_name
            os.environ["AGENT_CAPABILITIES"] = ",".join(config.capabilities)
            
            logger.info(f"Instantiating AutonomousAgent (worker): {config.name}")
            return AutonomousAgent(
                name=config.name,
                policy_name=config.policy_name,
                capabilities=config.capabilities
            )
        
        elif role == "bad_worker":
            os.environ["AGENT_PRIVATE_KEY"] = config.private_key
            os.environ["AGENT_NAME"] = config.name
            os.environ["AGENT_POLICY"] = config.policy_name
            os.environ["AGENT_CAPABILITIES"] = ",".join(config.capabilities)
            
            # Get failure rate from environment or use default
            failure_rate = float(os.getenv("AGENT_FAILURE_RATE", "0.4"))
            
            logger.info(f"Instantiating BadWorkerAgent: {config.name}")
            return BadWorkerAgent(
                name=config.name,
                policy_name=config.policy_name,
                capabilities=config.capabilities,
                failure_rate=failure_rate
            )
        
        elif role == "verifier":
            os.environ["VERIFIER_PRIVATE_KEY"] = config.private_key
            os.environ["VERIFIER_NAME"] = config.name
            
            # Get verifier mode from environment or use default
            verifier_mode = os.getenv("VERIFIER_MODE", "owner")
            
            logger.info(f"Instantiating VerifierAgent: {config.name}")
            return VerifierAgent(
                name=config.name,
                verifier_mode=verifier_mode
            )
        
        else:
            raise ValueError(f"Unknown agent role: {role}. Must be one of: buyer, worker, bad_worker, verifier")
    
    def load_and_start_agents(self) -> None:
        """Load agent configurations and start all agents."""
        logger.info("="*70)
        logger.info("AUTONOMOUS AGENT ECONOMY - STARTING")
        logger.info("="*70)
        
        # Load configurations from environment
        configs = load_agent_configs_from_env(prefix="AGENT")
        
        if not configs:
            logger.error("No agent configurations found!")
            logger.error("Please set environment variables in format:")
            logger.error("  AGENT_1_NAME=BuyerBot")
            logger.error("  AGENT_1_PRIVATE_KEY=0x...")
            logger.error("  AGENT_1_ROLE=buyer")
            logger.error("  AGENT_1_POLICY=ConservativePolicy")
            logger.error("  etc.")
            sys.exit(1)
        
        logger.info(f"Loaded {len(configs)} agent configuration(s)")
        logger.info("-"*70)
        
        # Instantiate and start each agent
        for config in configs:
            try:
                # Instantiate agent
                agent = self.instantiate_agent(config)
                
                # Create runner
                runner = AgentRunner(agent, config, self.interval_seconds)
                
                # Start agent thread
                runner.start()
                
                # Track runner
                self.runners.append(runner)
                
            except Exception as e:
                logger.error(f"Failed to start agent {config.name}: {e}", exc_info=True)
        
        logger.info("-"*70)
        logger.info(f"✓ Started {len(self.runners)} agent(s)")
        logger.info("="*70)
        
        # Summary
        self._print_summary()
    
    def _print_summary(self) -> None:
        """Print summary of running agents."""
        logger.info("\nEconomy Status:")
        logger.info("-"*70)
        
        role_counts = {}
        for runner in self.runners:
            role = runner.config.role
            role_counts[role] = role_counts.get(role, 0) + 1
        
        for role, count in sorted(role_counts.items()):
            logger.info(f"  {role.title()}: {count}")
        
        logger.info("-"*70)
        logger.info(f"Polling Interval: {self.interval_seconds} seconds")
        logger.info("Press Ctrl+C to stop all agents")
        logger.info("="*70)
    
    def wait(self) -> None:
        """Wait for all agent threads to complete (or Ctrl+C)."""
        try:
            # Keep main thread alive
            while True:
                # Check if any runners have stopped
                active_count = sum(1 for r in self.runners if r.running)
                
                if active_count == 0:
                    logger.warning("All agents have stopped")
                    break
                
                time.sleep(5)
        
        except KeyboardInterrupt:
            logger.info("\n" + "="*70)
            logger.info("SHUTDOWN REQUESTED")
            logger.info("="*70)
            self.stop_all()
    
    def stop_all(self) -> None:
        """Stop all running agents."""
        logger.info("Stopping all agents...")
        
        for runner in self.runners:
            try:
                runner.stop()
            except Exception as e:
                logger.error(f"Error stopping {runner.config.name}: {e}")
        
        logger.info("✓ All agents stopped")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run autonomous agent economy with buyers, workers, and verifiers"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Polling interval in seconds (default: 15)"
    )
    
    args = parser.parse_args()
    
    # Create and start economy
    economy = EconomyRunner(interval_seconds=args.interval)
    
    try:
        economy.load_and_start_agents()
        economy.wait()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        economy.stop_all()
        sys.exit(1)


if __name__ == "__main__":
    main()
