import time
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from onchain_reader import TokenBalance, LPPosition

class SampleDataManager:
    """Manages realistic sample data that can be easily updated with real data later."""
    
    def __init__(self):
        self.base_prices = {
            "ETH": 2000.0,
            "WETH": 2000.0,
            "USDC": 1.0,
            "USDT": 1.0,
            "DAI": 1.0,
            "WBTC": 45000.0,
            "LINK": 15.0,
            "UNI": 8.0,
            "AAVE": 120.0
        }
        
        self.price_volatility = {
            "ETH": 0.02,  # 2% volatility
            "WETH": 0.02,
            "USDC": 0.001,
            "USDT": 0.001,
            "DAI": 0.001,
            "WBTC": 0.03,
            "LINK": 0.04,
            "UNI": 0.05,
            "AAVE": 0.06
        }
        
        self.last_update = time.time()
        self.update_interval = 30  # Update prices every 30 seconds
        
        # Sample LP positions that mimic real Uniswap V3 positions
        self.sample_positions = self._create_sample_positions()
    
    def _create_sample_positions(self) -> List[LPPosition]:
        """Create realistic sample LP positions."""
        positions = []
        
        # Position 1: ETH/USDC pool (most common)
        positions.append(LPPosition(
            nft_id=19542083,
            token0=TokenBalance(
                symbol="ETH",
                address="0x4200000000000000000000000000000000000006",  # WETH on Base
                balance=2.5,
                usd_value=5000.0,
                price_usd=2000.0,
                decimals=18
            ),
            token1=TokenBalance(
                symbol="USDC",
                address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC on Base
                balance=5000.0,
                usd_value=5000.0,
                price_usd=1.0,
                decimals=6
            ),
            pool_address="0x4C36388bE6F416A29C8d8ED537Dd4fBA5b4bE4e9",
            fee_tier=500,  # 0.05%
            tick_lower=-887220,
            tick_upper=887220,
            liquidity=1000000,
            uncollected_fees_token0=0.05,
            uncollected_fees_token1=25.0,
            in_range=True,
            total_usd_value=10000.0,
            current_tick=0,
            sqrt_price_x96=0
        ))
        
        # Position 2: WBTC/ETH pool
        positions.append(LPPosition(
            nft_id=19542084,
            token0=TokenBalance(
                symbol="WBTC",
                address="0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",
                balance=0.1,
                usd_value=4500.0,
                price_usd=45000.0,
                decimals=8
            ),
            token1=TokenBalance(
                symbol="ETH",
                address="0x4200000000000000000000000000000000000006",
                balance=2.25,
                usd_value=4500.0,
                price_usd=2000.0,
                decimals=18
            ),
            pool_address="0x4C36388bE6F416A29C8d8ED537Dd4fBA5b4bE4e9",
            fee_tier=3000,  # 0.3%
            tick_lower=-276325,
            tick_upper=276325,
            liquidity=500000,
            uncollected_fees_token0=0.001,
            uncollected_fees_token1=0.1,
            in_range=True,
            total_usd_value=9000.0,
            current_tick=0,
            sqrt_price_x96=0
        ))
        
        # Position 3: LINK/USDC pool (out of range)
        positions.append(LPPosition(
            nft_id=19542085,
            token0=TokenBalance(
                symbol="LINK",
                address="0x514910771AF9Ca656af840dff83E8264EcF986CA",
                balance=300.0,
                usd_value=4500.0,
                price_usd=15.0,
                decimals=18
            ),
            token1=TokenBalance(
                symbol="USDC",
                address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                balance=3000.0,
                usd_value=3000.0,
                price_usd=1.0,
                decimals=6
            ),
            pool_address="0x4C36388bE6F416A29C8d8ED537Dd4fBA5b4bE4e9",
            fee_tier=500,  # 0.05%
            tick_lower=-887220,
            tick_upper=887220,
            liquidity=200000,
            uncollected_fees_token0=2.0,
            uncollected_fees_token1=50.0,
            in_range=False,  # Out of range
            total_usd_value=7500.0,
            current_tick=1000000,  # Way out of range
            sqrt_price_x96=0
        ))
        
        return positions
    
    def update_prices(self):
        """Simulate realistic price movements."""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        
        self.last_update = current_time
        
        # Simulate realistic price movements
        for token, base_price in self.base_prices.items():
            if token in ["USDC", "USDT", "DAI"]:
                # Stablecoins stay stable
                continue
            
            volatility = self.price_volatility.get(token, 0.02)
            # Random walk with mean reversion
            change = random.gauss(0, volatility)
            new_price = base_price * (1 + change)
            
            # Ensure prices stay reasonable
            if token in ["ETH", "WETH"]:
                new_price = max(1500, min(3000, new_price))
            elif token == "WBTC":
                new_price = max(35000, min(55000, new_price))
            elif token == "LINK":
                new_price = max(10, min(20, new_price))
            
            self.base_prices[token] = new_price
    
    def get_positions(self) -> List[LPPosition]:
        """Get current positions with updated prices."""
        self.update_prices()
        
        # Update positions with new prices
        updated_positions = []
        for pos in self.sample_positions:
            # Update token prices
            pos.token0.price_usd = self.base_prices.get(pos.token0.symbol, pos.token0.price_usd)
            pos.token1.price_usd = self.base_prices.get(pos.token1.symbol, pos.token1.price_usd)
            
            # Recalculate USD values
            pos.token0.usd_value = pos.token0.balance * pos.token0.price_usd
            pos.token1.usd_value = pos.token1.balance * pos.token1.price_usd
            
            # Update total value
            pos.total_usd_value = pos.token0.usd_value + pos.token1.usd_value
            
            # Simulate fee accumulation
            if pos.in_range:
                # In-range positions earn fees
                pos.uncollected_fees_token0 += random.uniform(0.001, 0.01)
                pos.uncollected_fees_token1 += random.uniform(1, 10)
            
            updated_positions.append(pos)
        
        return updated_positions
    
    def get_market_data(self) -> Dict[str, Any]:
        """Get current market data."""
        return {
            "timestamp": datetime.now().isoformat(),
            "prices": self.base_prices.copy(),
            "total_positions": len(self.sample_positions),
            "total_value": sum(pos.total_usd_value for pos in self.sample_positions),
            "in_range_positions": sum(1 for pos in self.sample_positions if pos.in_range),
            "out_of_range_positions": sum(1 for pos in self.sample_positions if not pos.in_range)
        }
    
    def simulate_trade(self, token: str, amount: float, direction: str):
        """Simulate a hedging trade (for testing)."""
        if token in self.base_prices:
            # Simulate price impact
            impact = 0.001 * amount / 1000  # 0.1% impact per $1000
            if direction == "buy":
                self.base_prices[token] *= (1 + impact)
            else:
                self.base_prices[token] *= (1 - impact)
    
    def replace_with_real_data(self, real_positions: List[LPPosition]):
        """Replace sample data with real blockchain data."""
        self.sample_positions = real_positions
        print("Sample data replaced with real blockchain data")
    
    def update_prices_from_feed(self, price_feed: Dict[str, float]):
        """Update prices from external price feed."""
        self.base_prices.update(price_feed)
        print("Prices updated from external feed")

# Global sample data manager
sample_data_manager = SampleDataManager()

def get_sample_data_manager() -> SampleDataManager:
    """Get the global sample data manager."""
    return sample_data_manager 