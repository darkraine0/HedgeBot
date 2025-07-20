# The Hedger - Automated LP Position Hedging Bot

A production-grade hedging bot that keeps the net dollar delta of LP-NFT positions within ±$50 by trading perpetual futures on Hyperliquid.

## Phase 1 Implementation

This is the Phase 1 implementation focusing on:
- Config loader + secure API key handling
- On-chain reader for LP-NFTs
- Basic delta calculator
- Simple web dashboard showing live balances + delta

## Project Structure

```
HedgeBot/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main FastAPI application
│   ├── config.py           # Configuration loader
│   ├── onchain_reader.py   # On-chain data reader
│   ├── delta_calculator.py # Delta calculation logic
│   ├── scheduler.py        # Adaptive task scheduler
│   ├── requirements.txt    # Python dependencies
│   └── venv/              # Virtual environment
└── frontend/               # React + Vite frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── App.jsx         # Main app component
    │   └── main.jsx        # React entry point
    ├── package.json        # Node.js dependencies
    ├── vite.config.js      # Vite configuration
    └── tailwind.config.js  # Tailwind CSS configuration
```

## Features

### Backend (FastAPI)

#### Configuration System
- YAML-based configuration with environment variable overrides
- Secure API key handling via environment variables
- Configuration validation and hash verification
- Support for multiple blockchain networks

#### On-Chain Reader
- LP-NFT position reading from Base network
- Token balance and uncollected fees tracking
- Pool state monitoring (tick ranges, liquidity)
- Real-time position updates

#### Delta Calculator
- Single-token hedging support (ETH/USDC)
- Net delta calculation with confidence scoring
- Hedge recommendation engine
- Configurable delta thresholds

#### Adaptive Scheduler
- Asynchronous task management
- Configurable intervals for different tasks
- Error handling and retry logic
- Task status monitoring

#### API Endpoints
- `/api/state` - Bot state and metrics
- `/api/positions` - LP position data
- `/api/delta` - Delta calculations
- `/api/tasks` - Task status
- `/api/config` - Configuration
- `/api/start` - Start bot
- `/api/stop` - Stop bot
- `/api/hedge-recommendation` - Hedge recommendations
- `/health` - Health check
- `/metrics` - Prometheus metrics

### Frontend (React + Vite + Tailwind CSS)

#### Dashboard
- Real-time bot status monitoring
- Key metrics display (LP value, delta, positions)
- Task status overview
- Auto-refresh functionality

#### Position Management
- Detailed LP position display
- Token balance tracking
- Range status monitoring
- Fee collection tracking

#### Delta Analysis
- Net delta visualization
- Token exposure breakdown
- Hedge recommendation display
- Confidence scoring

#### Task Monitoring
- Real-time task status
- Error tracking and display
- Performance metrics
- System health overview

#### Configuration
- Current settings display
- Risk management parameters
- Blockchain configuration
- Dashboard settings

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create configuration file:
```bash
# The config.py will create a default config.yaml file
python -c "from config import config_loader; config_loader.load_config()"
```

5. Update the configuration:
Edit `config.yaml` with your settings:
```yaml
blockchain:
  chain_id: 8453
  rpc_url: "https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
  wallet_address: "0xca63eB7BcD121FE5B0B74960D7F940f58344ABf7"

hedging:
  delta_threshold: 50.0
  rebalance_window: 30
  max_slippage: 0.5

risk:
  max_leverage: 8.0
  funding_cap_apr: 12.0
  impermanent_loss_cap: 20.0

hyperliquid:
  api_key: "YOUR_HYPERLIQUID_API_KEY"
  api_secret: "YOUR_HYPERLIQUID_API_SECRET"
  testnet: false
```

6. Set environment variables (optional):
```bash
export BLOCKCHAIN_RPC_URL="your_rpc_url"
export BLOCKCHAIN_WALLET_ADDRESS="your_wallet_address"
export HYPERLIQUID_API_KEY="your_api_key"
export HYPERLIQUID_API_SECRET="your_api_secret"
```

7. Run the backend:
```bash
python main.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### Starting the Bot

1. Start the backend server (see installation above)
2. Open the frontend dashboard in your browser
3. Click "Start" to begin the hedging bot
4. Monitor the dashboard for real-time updates

### Dashboard Features

- **Dashboard Tab**: Overview of bot status, key metrics, and delta analysis
- **Positions Tab**: Detailed view of LP positions and token balances
- **Delta Tab**: Delta calculations and hedge recommendations
- **Tasks Tab**: Task monitoring and system health
- **Config Tab**: Current configuration settings

### Configuration

The bot can be configured through:
1. `config.yaml` file in the backend directory
2. Environment variables (for sensitive data)
3. Dashboard configuration display

### Monitoring

- Real-time metrics via `/metrics` endpoint
- Health checks via `/health` endpoint
- Task status monitoring
- Error tracking and logging

## API Documentation

### Core Endpoints

#### GET `/api/state`
Returns the current bot state including:
- Running status
- Current delta calculation
- Position count and total value
- Task status

#### GET `/api/positions`
Returns LP position data:
- Token balances and prices
- Uncollected fees
- Range status
- Pool information

#### GET `/api/delta`
Returns delta calculation:
- Net delta value
- Token exposures
- Hedge recommendations
- Confidence scores

#### POST `/api/start`
Starts the hedging bot

#### POST `/api/stop`
Stops the hedging bot

#### GET `/api/hedge-recommendation`
Returns current hedge recommendation:
- Action (buy/sell/hold)
- Amount and token
- Urgency level
- Reasoning

## Development

### Backend Development

The backend is built with:
- **FastAPI**: Modern Python web framework
- **Web3.py**: Ethereum blockchain interaction
- **Pydantic**: Data validation
- **Asyncio**: Asynchronous programming
- **Uvicorn**: ASGI server

### Frontend Development

The frontend is built with:
- **React 18**: Modern React with hooks
- **Vite**: Fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Lucide React**: Icon library

### Architecture

The system follows a modular architecture:
- **Config Module**: Configuration management
- **On-Chain Reader**: Blockchain data fetching
- **Delta Calculator**: Hedging logic
- **Scheduler**: Task management
- **API Layer**: RESTful endpoints
- **Frontend**: React dashboard

## Security

- API keys stored in environment variables
- Configuration hash verification
- Secure WebSocket connections
- Input validation and sanitization
- Error handling without sensitive data exposure

## Phase 1 Limitations

This is Phase 1 implementation with the following limitations:
- Uses sample data for demonstration
- No actual trading execution
- Limited to ETH/USDC pairs
- Basic price feeds (static)
- No real Hyperliquid integration yet

## Next Steps (Phase 2)

Phase 2 will include:
- Hyperliquid perp adapter (WebSocket + REST)
- Hedge planner + order executor
- Simple alerts (Telegram for criticals)
- Real trading execution

## Support

For issues or questions:
1. Check the configuration settings
2. Review the logs in the backend
3. Verify API keys and network connectivity
4. Check the health endpoint for system status

## License

This project is proprietary software for automated trading. Use at your own risk. 