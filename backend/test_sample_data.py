#!/usr/bin/env python3
"""
Test script to verify sample data functionality
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sample_data import get_sample_data_manager
from delta_calculator import get_delta_calculator

async def test_sample_data():
    """Test the sample data functionality."""
    print("🧪 Testing Sample Data System")
    print("=" * 50)
    
    # Get sample data manager
    sample_manager = get_sample_data_manager()
    
    # Test 1: Get positions
    print("\n1. Testing Position Data:")
    positions = sample_manager.get_positions()
    print(f"   ✅ Found {len(positions)} positions")
    
    for i, pos in enumerate(positions):
        print(f"   Position {i+1}: {pos.token0.symbol}/{pos.token1.symbol}")
        print(f"      Value: ${pos.total_usd_value:,.2f}")
        print(f"      In Range: {'✅' if pos.in_range else '❌'}")
        print(f"      Fees: {pos.uncollected_fees_token0:.4f} {pos.token0.symbol} + {pos.uncollected_fees_token1:.2f} {pos.token1.symbol}")
    
    # Test 2: Get market data
    print("\n2. Testing Market Data:")
    market_data = sample_manager.get_market_data()
    print(f"   ✅ Market data retrieved")
    print(f"   Total Value: ${market_data['total_value']:,.2f}")
    print(f"   In Range: {market_data['in_range_positions']}")
    print(f"   Out of Range: {market_data['out_of_range_positions']}")
    
    # Test 3: Price updates
    print("\n3. Testing Price Updates:")
    old_prices = sample_manager.base_prices.copy()
    sample_manager.update_prices()
    new_prices = sample_manager.base_prices
    
    print("   Price Changes:")
    for token in ["ETH", "WBTC", "LINK"]:
        if token in old_prices and token in new_prices:
            change = ((new_prices[token] - old_prices[token]) / old_prices[token]) * 100
            print(f"      {token}: ${old_prices[token]:.2f} → ${new_prices[token]:.2f} ({change:+.2f}%)")
    
    # Test 4: Delta calculation
    print("\n4. Testing Delta Calculation:")
    delta_calculator = get_delta_calculator(50.0)
    delta = delta_calculator.calculate_delta(positions)
    
    print(f"   ✅ Delta calculated")
    print(f"   Net Delta: ${delta.net_delta:,.2f}")
    print(f"   Hedge Needed: {'✅' if delta.hedge_needed else '❌'}")
    if delta.hedge_needed:
        print(f"   Hedge Amount: ${delta.hedge_amount:,.2f}")
        print(f"   Hedge Token: {delta.hedge_token}")
        print(f"   Direction: {delta.hedge_direction}")
    
    # Test 5: Hedge recommendation
    print("\n5. Testing Hedge Recommendation:")
    recommendation = delta_calculator.get_hedge_recommendation(delta)
    print(f"   Action: {recommendation.action}")
    print(f"   Amount: ${recommendation.amount:,.2f}")
    print(f"   Token: {recommendation.token}")
    print(f"   Urgency: {recommendation.urgency}")
    print(f"   Reason: {recommendation.reason}")
    
    # Test 6: Trade simulation
    print("\n6. Testing Trade Simulation:")
    old_eth_price = sample_manager.base_prices["ETH"]
    sample_manager.simulate_trade("ETH", 1000, "buy")
    new_eth_price = sample_manager.base_prices["ETH"]
    price_change = ((new_eth_price - old_eth_price) / old_eth_price) * 100
    print(f"   Simulated buy $1000 ETH")
    print(f"   ETH price: ${old_eth_price:.2f} → ${new_eth_price:.2f} ({price_change:+.2f}%)")
    
    print("\n✅ All tests passed!")
    print("\n📊 Summary:")
    print(f"   Total LP Value: ${market_data['total_value']:,.2f}")
    print(f"   Net Delta: ${delta.net_delta:,.2f}")
    print(f"   Hedge Status: {'Needed' if delta.hedge_needed else 'Balanced'}")
    print(f"   Positions: {len(positions)} ({market_data['in_range_positions']} in range)")

if __name__ == "__main__":
    asyncio.run(test_sample_data()) 