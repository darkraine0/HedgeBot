import asyncio
import time
from typing import List, Dict, Any, Optional
from web3 import Web3
from web3.exceptions import ContractLogicError
from pydantic import BaseModel
import json

# Uniswap V3 ABI (minimal for LP-NFT reading)
UNISWAP_V3_POSITION_ABI = [
    {
        "inputs": [],
        "name": "positions",
        "outputs": [
            {"internalType": "uint96", "name": "nonce", "type": "uint96"},
            {"internalType": "address", "name": "operator", "type": "address"},
            {"internalType": "address", "name": "token0", "type": "address"},
            {"internalType": "address", "name": "token1", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"},
            {"internalType": "int24", "name": "tickLower", "type": "int24"},
            {"internalType": "int24", "name": "tickUpper", "type": "int24"},
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "feeGrowthInside0LastX128", "type": "uint256"},
            {"internalType": "uint256", "name": "feeGrowthInside1LastX128", "type": "uint256"},
            {"internalType": "uint128", "name": "tokensOwed0", "type": "uint128"},
            {"internalType": "uint128", "name": "tokensOwed1", "type": "uint128"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC20 ABI (minimal for token reading)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

# Uniswap V3 Pool ABI (minimal for price reading)
UNISWAP_V3_POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

class TokenBalance(BaseModel):
    symbol: str
    address: str
    balance: float
    usd_value: float
    price_usd: float
    decimals: int

class LPPosition(BaseModel):
    nft_id: int
    token0: TokenBalance
    token1: TokenBalance
    pool_address: str
    fee_tier: int
    tick_lower: int
    tick_upper: int
    liquidity: int
    uncollected_fees_token0: float
    uncollected_fees_token1: float
    in_range: bool
    total_usd_value: float
    current_tick: int
    sqrt_price_x96: int

class OnChainReader:
    def __init__(self, rpc_url: str, wallet_address: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.wallet_address = wallet_address
        # Base Uniswap V3 Position Manager - ensure checksummed
        self.position_manager_address = self.w3.to_checksum_address("0x03a520b3c5f8d0b3a7400d6f8e0e396e0325c3d6")
        self.last_block = 0
        self.last_refresh = 0
        
        # Token price cache (in production, use a price oracle)
        self.token_prices = {
            "ETH": 2000.0,  # Will be updated from price feeds
            "USDC": 1.0,
            "WETH": 2000.0
        }
    
    async def get_lp_positions(self, nft_ids: List[int]) -> List[LPPosition]:
        """Fetch LP positions for given NFT IDs."""
        positions = []
        
        for nft_id in nft_ids:
            try:
                position = await self._get_single_position(nft_id)
                if position:
                    positions.append(position)
            except Exception as e:
                print(f"Error fetching position {nft_id}: {e}")
                continue
        
        return positions
    
    async def _get_single_position(self, nft_id: int) -> Optional[LPPosition]:
        """Fetch a single LP position."""
        try:
            # Get position manager contract
            position_manager = self.w3.eth.contract(
                address=self.position_manager_address,
                abi=UNISWAP_V3_POSITION_ABI
            )
            
            # Get position data
            position_data = position_manager.functions.positions(nft_id).call()
            
            # Extract position info
            token0_address = position_data[2]
            token1_address = position_data[3]
            fee_tier = position_data[4]
            tick_lower = position_data[5]
            tick_upper = position_data[6]
            liquidity = position_data[7]
            tokens_owed0 = position_data[10]
            tokens_owed1 = position_data[11]
            
            # Get token balances and info
            token0 = await self._get_token_info(token0_address, tokens_owed0)
            token1 = await self._get_token_info(token1_address, tokens_owed1)
            
            # Get pool address and current state
            pool_address = self._get_pool_address(token0_address, token1_address, fee_tier)
            current_tick, sqrt_price_x96 = await self._get_pool_state(pool_address)
            
            # Check if position is in range
            in_range = tick_lower <= current_tick <= tick_upper
            
            # Calculate total value
            total_value = token0.usd_value + token1.usd_value
            
            return LPPosition(
                nft_id=nft_id,
                token0=token0,
                token1=token1,
                pool_address=pool_address,
                fee_tier=fee_tier,
                tick_lower=tick_lower,
                tick_upper=tick_upper,
                liquidity=liquidity,
                uncollected_fees_token0=token0.balance,
                uncollected_fees_token1=token1.balance,
                in_range=in_range,
                total_usd_value=total_value,
                current_tick=current_tick,
                sqrt_price_x96=sqrt_price_x96
            )
            
        except Exception as e:
            print(f"Error fetching position {nft_id}: {e}")
            return None
    
    async def _get_token_info(self, token_address: str, tokens_owed: int) -> TokenBalance:
        """Get token information and balance."""
        try:
            # Ensure address is checksummed
            token_address_checksum = self.w3.to_checksum_address(token_address)
            
            token_contract = self.w3.eth.contract(
                address=token_address_checksum,
                abi=ERC20_ABI
            )
            
            # Get token info
            symbol = token_contract.functions.symbol().call()
            decimals = token_contract.functions.decimals().call()
            
            # Get balance (including owed tokens)
            balance_raw = tokens_owed
            balance = balance_raw / (10 ** decimals)
            
            # Get USD price (in production, use price oracle)
            price_usd = self.token_prices.get(symbol, 0.0)
            usd_value = balance * price_usd
            
            return TokenBalance(
                symbol=symbol,
                address=token_address,
                balance=balance,
                usd_value=usd_value,
                price_usd=price_usd,
                decimals=decimals
            )
            
        except Exception as e:
            print(f"Error getting token info for {token_address}: {e}")
            # Return default token info
            return TokenBalance(
                symbol="UNKNOWN",
                address=token_address,
                balance=0.0,
                usd_value=0.0,
                price_usd=0.0,
                decimals=18
            )
    
    def _get_pool_address(self, token0: str, token1: str, fee: int) -> str:
        """Get pool address for token pair and fee tier."""
        try:
            # Ensure addresses are checksummed
            token0_checksum = self.w3.to_checksum_address(token0)
            token1_checksum = self.w3.to_checksum_address(token1)
            
            # This is a simplified version - in production, use Uniswap V3 factory
            # For now, return a placeholder but with proper checksum handling
            # In real implementation, you would use the Uniswap V3 factory to compute pool address
            return f"0x{'0' * 40}"
        except Exception as e:
            print(f"Error getting pool address: {e}")
            return f"0x{'0' * 40}"
    
    async def _get_pool_state(self, pool_address: str) -> tuple[int, int]:
        """Get current pool state (tick and sqrt price)."""
        try:
            pool_contract = self.w3.eth.contract(
                address=pool_address,
                abi=UNISWAP_V3_POOL_ABI
            )
            
            slot0 = pool_contract.functions.slot0().call()
            current_tick = slot0[1]
            sqrt_price_x96 = slot0[0]
            
            return current_tick, sqrt_price_x96
            
        except Exception as e:
            print(f"Error getting pool state: {e}")
            return 0, 0
    
    async def get_wallet_positions(self) -> List[int]:
        """Get all LP-NFT IDs owned by the wallet."""
        # This would require scanning for Transfer events or using an indexer
        # For now, return the known NFT ID
        return [19542083]
    
    def update_token_prices(self, prices: Dict[str, float]):
        """Update token prices from external price feed."""
        self.token_prices.update(prices)
    
    def get_last_block(self) -> int:
        """Get the last processed block number."""
        return self.last_block
    
    def get_last_refresh(self) -> float:
        """Get the last refresh timestamp."""
        return self.last_refresh

# Global on-chain reader instance
onchain_reader = None

def get_onchain_reader(rpc_url: str, wallet_address: str) -> OnChainReader:
    """Get or create on-chain reader instance."""
    global onchain_reader
    if onchain_reader is None:
        onchain_reader = OnChainReader(rpc_url, wallet_address)
    return onchain_reader 