import os
from typing import Optional
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount


class WalletSigner:
    """Manages agent private key, address, and transaction signing on Monad."""

    def __init__(self, rpc_url: Optional[str] = None, private_key: Optional[str] = None):
        self.rpc_url = rpc_url or os.getenv("MONAD_RPC_URL", "https://testnet-rpc.monad.xyz")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        pk = private_key or os.getenv("AGENT_PRIVATE_KEY")
        if pk:
            self.account: Optional[LocalAccount] = Account.from_key(pk)
            self.address = self.account.address
        else:
            # Fallback generation for testing/development
            self.account = None
            self.address = "0x0000000000000000000000000000000000000000"

    def get_balance(self) -> int:
        """Fetch native MON balance in wei."""
        if not self.w3.is_connected() or self.address == "0x0000000000000000000000000000000000000000":
            return 0
        try:
            return self.w3.eth.get_balance(self.address)
        except Exception:
            return 0

    def sign_and_send_transaction(self, tx_params: dict) -> Optional[str]:
        """Sign and broadcast transaction using agent's private key."""
        if not self.account:
            raise ValueError("Agent private key not configured. Cannot sign transaction.")
        
        tx_params["from"] = self.address
        tx_params["nonce"] = self.w3.eth.get_transaction_count(self.address)
        if "chainId" not in tx_params:
            tx_params["chainId"] = int(os.getenv("MONAD_CHAIN_ID", 10143))
        
        signed_tx = self.account.sign_transaction(tx_params)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.w3.to_hex(tx_hash)
