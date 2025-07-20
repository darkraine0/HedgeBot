from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import time
import random
from datetime import datetime, timedelta
import logging

# Import our modules
from config import config_loader
from onchain_reader import get_onchain_reader, LPPosition
from delta_calculator import get_delta_calculator, DeltaCalculation, HedgeRecommendation
from scheduler import get_scheduler, TaskStatus

# Create FastAPI app
app = FastAPI(
    title="The Hedger Bot API",
    description="Automated LP Position Hedging Bot - Phase 1",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class TokenBalance(BaseModel):
    symbol: str
    address: str
    balance: float
    usd_value: float
    price_usd: float

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

class DeltaCalculation(BaseModel):
    total_lp_value: float
    token0_exposure: float
    token1_exposure: float
    net_delta: float
    hedge_needed: bool
    hedge_amount: float
    hedge_token: str

class TaskStatus(BaseModel):
    name: str
    running: bool
    last_run: float
    error_count: int
    last_error: Optional[str]
    interval: int

class BotState(BaseModel):
    running: bool
    current_delta: Optional[DeltaCalculation]
    position_count: int
    total_lp_value: float
    task_status: Dict[str, TaskStatus]

# Global state
current_positions: List[LPPosition] = []
current_delta: Optional[DeltaCalculation] = None
config = None
onchain_reader = None
delta_calculator = None
scheduler = None

# Initialize components
def initialize_components():
    """Initialize all components with configuration."""
    global config, onchain_reader, delta_calculator, scheduler
    
    try:
        # Load configuration
        config = config_loader.load_config()
        
        # Initialize on-chain reader
        onchain_reader = get_onchain_reader(
            config.blockchain.rpc_url,
            config.blockchain.wallet_address
        )
        
        # Initialize delta calculator
        delta_calculator = get_delta_calculator(config.hedging.delta_threshold)
        
        # Initialize scheduler
        scheduler = get_scheduler()
        
        # Add scheduled tasks
        scheduler.add_task(
            "delta_check",
            delta_check_task,
            config.hedging.rebalance_window,
            "Delta calculation check"
        )
        
        scheduler.add_task(
            "position_update",
            position_update_task,
            30,  # 30 seconds
            "LP position update"
        )
        
        scheduler.add_task(
            "onchain_refresh",
            onchain_refresh_task,
            4,  # 4 seconds
            "On-chain data refresh"
        )
        
        logging.info("Components initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing components: {e}")
        # Create a basic scheduler even if config fails
        scheduler = get_scheduler()

# Scheduled tasks
async def delta_check_task():
    """Task to check and calculate delta."""
    global current_delta, current_positions
    
    if not current_positions:
        return
    
    try:
        current_delta = delta_calculator.calculate_delta(current_positions)
        logging.info(f"Delta calculated: {current_delta.net_delta:.2f}")
    except Exception as e:
        logging.error(f"Delta calculation failed: {e}")

async def position_update_task():
    """Task to update LP positions from sample data (or real data when available)."""
    global current_positions, onchain_reader, sample_data_manager
    
    try:
        if onchain_reader:
            # Try to get real positions first
            nft_ids = await onchain_reader.get_wallet_positions()
            if nft_ids:
                positions = await onchain_reader.get_lp_positions(nft_ids)
                current_positions = positions
                logging.info(f"Updated {len(positions)} real positions")
            else:
                # Fall back to sample data
                current_positions = sample_data_manager.get_positions()
                logging.info(f"Using {len(current_positions)} sample positions")
        else:
            # Use sample data
            current_positions = sample_data_manager.get_positions()
            logging.info(f"Updated {len(current_positions)} sample positions")
    except Exception as e:
        logging.error(f"Error updating positions: {e}")
        # Fall back to sample data
        current_positions = sample_data_manager.get_positions()

async def onchain_refresh_task():
    """Task to refresh on-chain data."""
    try:
        # Update token prices (in production, get from price oracle)
        # For now, we'll use static prices
        pass
    except Exception as e:
        logging.error(f"On-chain refresh failed: {e}")

# Initialize on startup
initialize_components()
logging.info("Backend initialization complete")

# Initialize sample data manager
from sample_data import get_sample_data_manager
sample_data_manager = get_sample_data_manager()

# Add some sample data for testing
if not current_positions:
    # Use realistic sample data
    current_positions = sample_data_manager.get_positions()

# API Routes
@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "The Hedger Bot API",
        "version": "1.0.0",
        "phase": "Phase 1 - Sample Data",
        "endpoints": {
            "/api/state": "Get current bot state",
            "/api/positions": "Get LP positions",
            "/api/delta": "Get delta calculation",
            "/api/tasks": "Get task status",
            "/health": "Health check",
            "/metrics": "Prometheus metrics"
        }
    }

@app.get("/api/state")
async def get_bot_state():
    """Get current bot state."""
    global current_positions, current_delta, scheduler
    
    try:
        # Get task status safely
        task_status = {}
        if scheduler:
            try:
                task_status = scheduler.get_all_task_status()
            except Exception as e:
                logging.error(f"Error getting task status: {e}")
                task_status = {}
        
        # Calculate total LP value safely
        total_lp_value = 0
        try:
            total_lp_value = sum(pos.total_usd_value for pos in current_positions)
        except Exception as e:
            logging.error(f"Error calculating total LP value: {e}")
        
        return BotState(
            running=scheduler.is_running() if scheduler else False,
            current_delta=current_delta,
            position_count=len(current_positions),
            total_lp_value=total_lp_value,
            task_status=task_status
        )
    except Exception as e:
        logging.error(f"Error in get_bot_state: {e}")
        # Return a safe default state
        return BotState(
            running=False,
            current_delta=None,
            position_count=0,
            total_lp_value=0.0,
            task_status={}
        )

@app.get("/api/positions")
async def get_positions():
    """Get current LP positions."""
    global current_positions
    
    try:
        total_value = sum(pos.total_usd_value for pos in current_positions)
        return {
            "positions": [pos.dict() for pos in current_positions],
            "count": len(current_positions),
            "total_value": total_value
        }
    except Exception as e:
        logging.error(f"Error in get_positions: {e}")
        return {
            "positions": [],
            "count": 0,
            "total_value": 0.0
        }

@app.get("/api/delta")
async def get_delta():
    """Get current delta calculation."""
    global current_delta, current_positions, delta_calculator
    
    try:
        if not current_delta and current_positions and delta_calculator:
            # Calculate delta if not available
            current_delta = delta_calculator.calculate_delta(current_positions)
        
        return current_delta.dict() if current_delta else {}
    except Exception as e:
        logging.error(f"Error in get_delta: {e}")
        return {}

@app.get("/api/tasks")
async def get_tasks():
    """Get task status."""
    global scheduler
    
    try:
        if scheduler:
            return scheduler.get_all_task_status()
        return {}
    except Exception as e:
        logging.error(f"Error in get_tasks: {e}")
        return {}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global scheduler, current_positions, current_delta
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time() - (scheduler.get_task_status("delta_check").last_run if scheduler else time.time()),
        "positions_count": len(current_positions),
        "delta_available": current_delta is not None,
        "scheduler_running": scheduler.is_running() if scheduler else False
    }

@app.get("/metrics")
async def get_metrics():
    """Prometheus-style metrics endpoint."""
    global current_positions, current_delta, scheduler
    
    metrics = [
        f"hedger_bot_running {1 if scheduler and scheduler.is_running() else 0}",
        f"hedger_positions_count {len(current_positions)}",
        f"hedger_total_lp_value {sum(pos.total_usd_value for pos in current_positions)}"
    ]
    
    if current_delta:
        metrics.extend([
            f"hedger_net_delta {current_delta.net_delta}",
            f"hedger_hedge_needed {1 if current_delta.hedge_needed else 0}",
            f"hedger_hedge_amount {current_delta.hedge_amount}"
        ])
    
    # Task metrics
    if scheduler:
        task_status = scheduler.get_all_task_status()
        for task_name, task in task_status.items():
            metrics.append(f'hedger_task_running{{task="{task_name}"}} {1 if task.running else 0}')
            metrics.append(f'hedger_task_errors{{task="{task_name}"}} {task.error_count}')
    
    return "\n".join(metrics)

@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    global config
    
    if config:
        return {
            "blockchain": {
                "chain_id": config.blockchain.chain_id,
                "rpc_url": config.blockchain.rpc_url,
                "wallet_address": config.blockchain.wallet_address
            },
            "hedging": {
                "delta_threshold": config.hedging.delta_threshold,
                "rebalance_window": config.hedging.rebalance_window,
                "max_slippage": config.hedging.max_slippage
            },
            "risk": {
                "max_leverage": config.risk.max_leverage,
                "funding_cap_apr": config.risk.funding_cap_apr,
                "impermanent_loss_cap": config.risk.impermanent_loss_cap
            },
            "dashboard": {
                "host": config.dashboard.host,
                "port": config.dashboard.port,
                "refresh_interval": config.dashboard.refresh_interval
            }
        }
    return {}

@app.post("/api/start")
async def start_bot():
    """Start the hedging bot."""
    global scheduler
    
    try:
        if scheduler and not scheduler.is_running():
            # Set scheduler as running
            scheduler.running = True
            # Start tasks in background without blocking
            for name, task_info in scheduler.tasks.items():
                if task_info["function"]:
                    asyncio.create_task(scheduler._run_task(name, task_info))
            
            return {"status": "started", "message": "Bot started successfully"}
        else:
            return {"status": "already_running", "message": "Bot is already running"}
    except Exception as e:
        logging.error(f"Error starting bot: {e}")
        return {"status": "error", "message": f"Failed to start bot: {str(e)}"}

@app.post("/api/stop")
async def stop_bot():
    """Stop the hedging bot."""
    global scheduler
    
    try:
        if scheduler and scheduler.is_running():
            scheduler.running = False
            return {"status": "stopped", "message": "Bot stopped successfully"}
        else:
            return {"status": "not_running", "message": "Bot is not running"}
    except Exception as e:
        logging.error(f"Error stopping bot: {e}")
        return {"status": "error", "message": f"Failed to stop bot: {str(e)}"}

@app.get("/api/hedge-recommendation")
async def get_hedge_recommendation():
    """Get current hedge recommendation."""
    global current_delta, delta_calculator
    
    if not current_delta:
        return {"error": "No delta calculation available"}
    
    recommendation = delta_calculator.get_hedge_recommendation(current_delta)
    return recommendation.dict()

@app.get("/api/market-data")
async def get_market_data():
    """Get current market data and prices."""
    global sample_data_manager
    
    try:
        return sample_data_manager.get_market_data()
    except Exception as e:
        logging.error(f"Error getting market data: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "prices": {},
            "total_positions": 0,
            "total_value": 0.0,
            "in_range_positions": 0,
            "out_of_range_positions": 0
        }

@app.post("/api/simulate-trade")
async def simulate_trade(request: dict):
    """Simulate a hedging trade (for testing)."""
    global sample_data_manager
    
    try:
        token = request.get("token", "ETH")
        amount = request.get("amount", 1000.0)
        direction = request.get("direction", "buy")
        
        sample_data_manager.simulate_trade(token, amount, direction)
        
        return {
            "status": "success",
            "message": f"Simulated {direction} {amount} {token}",
            "new_prices": sample_data_manager.base_prices
        }
    except Exception as e:
        logging.error(f"Error simulating trade: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 