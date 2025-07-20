# Sample Data System Guide

## Overview

The hedging bot now uses a **realistic sample data system** that mimics real LP-NFT positions and market conditions. This allows you to test the bot functionality immediately while waiting for real blockchain connection details.

## What's Included

### 1. **Realistic LP Positions**
- **3 Sample Positions** with different characteristics:
  - **ETH/USDC Pool**: $10,000 value, in-range, earning fees
  - **WBTC/ETH Pool**: $9,000 value, in-range, earning fees  
  - **LINK/USDC Pool**: $7,500 value, out-of-range, not earning fees

### 2. **Dynamic Price Simulation**
- **Realistic price movements** every 30 seconds
- **Token volatility** based on real market characteristics
- **Price impact simulation** when trades are executed

### 3. **Live Dashboard Updates**
- **Real-time data** updates every 10 seconds
- **Market overview** with position statistics
- **Delta calculations** with hedge recommendations

## How It Works

### Backend Components

#### `sample_data.py`
```python
# Main sample data manager
sample_data_manager = SampleDataManager()

# Get current positions with updated prices
positions = sample_data_manager.get_positions()

# Get market data
market_data = sample_data_manager.get_market_data()

# Simulate a trade
sample_data_manager.simulate_trade("ETH", 1000, "buy")
```

#### Key Features:
- **Price Updates**: Simulates realistic market movements
- **Fee Accumulation**: In-range positions earn fees over time
- **Trade Simulation**: Simulates price impact of hedging trades
- **Easy Replacement**: Can be swapped for real data later

### Frontend Display

The dashboard now shows:
- **Total LP Value**: $26,500 (sum of all positions)
- **Net Delta**: Real-time calculation of dollar exposure
- **Position Status**: In-range vs out-of-range positions
- **Market Data**: Live price updates and statistics
- **Hedge Recommendations**: When delta exceeds threshold

## Testing the System

### 1. **Start the Backend**
```bash
cd backend
venv\Scripts\activate
python main.py
```

### 2. **Start the Frontend**
```bash
cd frontend
npm install
npm run dev
```

### 3. **Test Sample Data**
```bash
cd backend
python test_sample_data.py
```

## Expected Output

### Dashboard Metrics:
- **Total LP Value**: ~$26,500
- **Positions**: 3 (2 in-range, 1 out-of-range)
- **Net Delta**: Varies based on price movements
- **Hedge Status**: Updates based on delta threshold

### Sample Positions:
1. **ETH/USDC**: $10,000, in-range, earning fees
2. **WBTC/ETH**: $9,000, in-range, earning fees
3. **LINK/USDC**: $7,500, out-of-range, not earning

## Replacing with Real Data

When you get the real blockchain connection details, you can easily replace the sample data:

### 1. **Update Configuration**
```python
# In config.yaml
blockchain:
  rpc_url: "https://mainnet.base.org"  # Your real RPC
  wallet_address: "0x..."              # Your wallet
```

### 2. **Replace Sample Data**
```python
# In main.py, replace sample data with real data
real_positions = await onchain_reader.get_lp_positions(nft_ids)
sample_data_manager.replace_with_real_data(real_positions)
```

### 3. **Add Real Price Feeds**
```python
# Update prices from real sources
real_prices = await get_price_feed()  # Your price oracle
sample_data_manager.update_prices_from_feed(real_prices)
```

## API Endpoints

### Current Endpoints:
- `/api/state` - Bot status and metrics
- `/api/positions` - LP position data
- `/api/delta` - Delta calculations
- `/api/market-data` - Market overview
- `/api/simulate-trade` - Test trade simulation

### Example Response:
```json
{
  "running": false,
  "current_delta": {
    "net_delta": 1250.0,
    "hedge_needed": true,
    "hedge_amount": 1250.0,
    "hedge_token": "ETH"
  },
  "position_count": 3,
  "total_lp_value": 26500.0
}
```

## Benefits

### ✅ **Immediate Testing**
- Test bot functionality without blockchain setup
- Verify dashboard and API endpoints
- Debug delta calculations and hedging logic

### ✅ **Realistic Data**
- Mimics real LP-NFT positions
- Simulates market price movements
- Shows fee accumulation and position status

### ✅ **Easy Migration**
- Drop-in replacement for real data
- Same API structure
- No frontend changes needed

### ✅ **Development Friendly**
- No blockchain dependencies for testing
- Fast iteration and debugging
- Predictable test scenarios

## Next Steps

1. **Test the current system** with sample data
2. **Verify dashboard functionality**
3. **Test start/stop bot functionality**
4. **When ready, replace with real blockchain data**

The sample data system provides a complete working prototype that can be easily upgraded to use real blockchain data when available. 