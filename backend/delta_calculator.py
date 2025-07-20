from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from onchain_reader import LPPosition, TokenBalance

class DeltaCalculation(BaseModel):
    total_lp_value: float
    token0_exposure: float
    token1_exposure: float
    net_delta: float
    hedge_needed: bool
    hedge_amount: float
    hedge_token: str
    hedge_direction: str  # "long" or "short"
    confidence: float  # 0-1 confidence in calculation

class HedgeRecommendation(BaseModel):
    action: str  # "buy", "sell", "hold"
    amount: float
    token: str
    urgency: str  # "low", "medium", "high"
    reason: str

class DeltaCalculator:
    def __init__(self, delta_threshold: float = 50.0):
        self.delta_threshold = delta_threshold
        
        # Token mapping for hedging (which tokens to hedge)
        self.hedge_tokens = {
            "ETH": True,  # Hedge ETH exposure
            "WETH": True,  # Hedge WETH exposure
            "USDC": False,  # Don't hedge USDC (stablecoin)
            "USDT": False,  # Don't hedge USDT (stablecoin)
            "DAI": False,   # Don't hedge DAI (stablecoin)
        }
        
        # Price sources (in production, use real price feeds)
        self.token_prices = {
            "ETH": 2000.0,
            "WETH": 2000.0,
            "USDC": 1.0,
            "USDT": 1.0,
            "DAI": 1.0
        }
    
    def calculate_delta(self, positions: List[LPPosition]) -> DeltaCalculation:
        """Calculate net delta from LP positions."""
        if not positions:
            return DeltaCalculation(
                total_lp_value=0.0,
                token0_exposure=0.0,
                token1_exposure=0.0,
                net_delta=0.0,
                hedge_needed=False,
                hedge_amount=0.0,
                hedge_token="ETH",
                hedge_direction="long",
                confidence=1.0
            )
        
        total_lp_value = sum(pos.total_usd_value for pos in positions)
        token0_exposure = 0.0
        token1_exposure = 0.0
        
        # Calculate exposures for each position
        for position in positions:
            # Token0 exposure (including uncollected fees)
            token0_total = position.token0.usd_value + (position.uncollected_fees_token0 * position.token0.price_usd)
            token0_exposure += token0_total
            
            # Token1 exposure (including uncollected fees)
            token1_total = position.token1.usd_value + (position.uncollected_fees_token1 * position.token1.price_usd)
            token1_exposure += token1_total
        
        # Calculate net delta (only for hedgeable tokens)
        net_delta = 0.0
        hedge_token = "ETH"  # Default hedge token
        
        # Check if we should hedge token0
        if self._should_hedge_token(position.token0.symbol):
            net_delta += token0_exposure
            hedge_token = position.token0.symbol
        
        # Check if we should hedge token1
        if self._should_hedge_token(position.token1.symbol):
            net_delta += token1_exposure
            if abs(token1_exposure) > abs(token0_exposure):
                hedge_token = position.token1.symbol
        
        # Determine if hedging is needed
        hedge_needed = abs(net_delta) > self.delta_threshold
        hedge_amount = abs(net_delta) if hedge_needed else 0.0
        hedge_direction = "short" if net_delta > 0 else "long"
        
        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(positions)
        
        return DeltaCalculation(
            total_lp_value=total_lp_value,
            token0_exposure=token0_exposure,
            token1_exposure=token1_exposure,
            net_delta=net_delta,
            hedge_needed=hedge_needed,
            hedge_amount=hedge_amount,
            hedge_token=hedge_token,
            hedge_direction=hedge_direction,
            confidence=confidence
        )
    
    def _should_hedge_token(self, token_symbol: str) -> bool:
        """Determine if a token should be hedged."""
        return self.hedge_tokens.get(token_symbol, False)
    
    def _calculate_confidence(self, positions: List[LPPosition]) -> float:
        """Calculate confidence in the delta calculation."""
        if not positions:
            return 0.0
        
        # Check if all positions have valid data
        valid_positions = 0
        total_positions = len(positions)
        
        for position in positions:
            # Check if position has valid token data
            if (position.token0.symbol != "UNKNOWN" and 
                position.token1.symbol != "UNKNOWN" and
                position.total_usd_value > 0):
                valid_positions += 1
        
        confidence = valid_positions / total_positions
        
        # Additional confidence factors
        if confidence > 0:
            # Check if positions are in range (more reliable data)
            in_range_count = sum(1 for pos in positions if pos.in_range)
            range_confidence = in_range_count / total_positions
            confidence = (confidence + range_confidence) / 2
        
        return min(confidence, 1.0)
    
    def get_hedge_recommendation(self, delta_calc: DeltaCalculation) -> HedgeRecommendation:
        """Get hedge recommendation based on delta calculation."""
        if not delta_calc.hedge_needed:
            return HedgeRecommendation(
                action="hold",
                amount=0.0,
                token=delta_calc.hedge_token,
                urgency="low",
                reason="Delta within threshold"
            )
        
        # Determine urgency based on delta size
        delta_ratio = delta_calc.hedge_amount / delta_calc.total_lp_value if delta_calc.total_lp_value > 0 else 0
        
        if delta_ratio > 0.1:  # >10% of total value
            urgency = "high"
        elif delta_ratio > 0.05:  # >5% of total value
            urgency = "medium"
        else:
            urgency = "low"
        
        # Determine action
        if delta_calc.net_delta > 0:
            action = "sell"  # Need to short
        else:
            action = "buy"   # Need to long
        
        return HedgeRecommendation(
            action=action,
            amount=delta_calc.hedge_amount,
            token=delta_calc.hedge_token,
            urgency=urgency,
            reason=f"Delta {delta_calc.net_delta:.2f} exceeds threshold {self.delta_threshold}"
        )
    
    def update_token_prices(self, prices: Dict[str, float]):
        """Update token prices from external source."""
        self.token_prices.update(prices)
    
    def update_delta_threshold(self, threshold: float):
        """Update delta threshold."""
        self.delta_threshold = threshold
    
    def get_hedge_tokens(self) -> Dict[str, bool]:
        """Get current hedge token configuration."""
        return self.hedge_tokens.copy()
    
    def set_hedge_tokens(self, hedge_config: Dict[str, bool]):
        """Update hedge token configuration."""
        self.hedge_tokens.update(hedge_config)

# Global delta calculator instance
delta_calculator = DeltaCalculator()

def get_delta_calculator(threshold: float = 50.0) -> DeltaCalculator:
    """Get or create delta calculator instance."""
    global delta_calculator
    if delta_calculator.delta_threshold != threshold:
        delta_calculator.update_delta_threshold(threshold)
    return delta_calculator 