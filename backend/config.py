import os
import yaml
import hashlib
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BlockchainConfig(BaseModel):
    chain_id: int = Field(default=8453, description="Base chain ID")
    rpc_url: str = Field(..., description="RPC endpoint URL")
    wallet_address: str = Field(..., description="Wallet address for LP-NFTs")
    private_key: Optional[str] = Field(default=None, description="Private key (from env)")

class HedgingConfig(BaseModel):
    delta_threshold: float = Field(default=50.0, description="Delta threshold in USD")
    rebalance_window: int = Field(default=30, description="Rebalance window in seconds")
    max_slippage: float = Field(default=0.5, description="Maximum slippage percentage")

class RiskConfig(BaseModel):
    max_leverage: float = Field(default=8.0, description="Maximum leverage")
    funding_cap_apr: float = Field(default=12.0, description="Funding APR cap")
    impermanent_loss_cap: float = Field(default=20.0, description="Impermanent loss cap")

class DashboardConfig(BaseModel):
    host: str = Field(default="0.0.0.0", description="Dashboard host")
    port: int = Field(default=8000, description="Dashboard port")
    refresh_interval: int = Field(default=15, description="Refresh interval in seconds")

class HyperliquidConfig(BaseModel):
    api_key: str = Field(..., description="Hyperliquid API key")
    api_secret: str = Field(..., description="Hyperliquid API secret")
    testnet: bool = Field(default=False, description="Use testnet")

class AlertConfig(BaseModel):
    telegram_token: Optional[str] = Field(default=None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(default=None, description="Telegram chat ID")
    slack_token: Optional[str] = Field(default=None, description="Slack bot token")
    slack_channel: Optional[str] = Field(default=None, description="Slack channel")

class Config(BaseModel):
    blockchain: BlockchainConfig
    hedging: HedgingConfig
    risk: RiskConfig
    dashboard: DashboardConfig
    hyperliquid: HyperliquidConfig
    alerts: AlertConfig

class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config: Optional[Config] = None
        self.config_hash: Optional[str] = None
    
    def load_config(self) -> Config:
        """Load configuration from YAML file and environment variables."""
        if not os.path.exists(self.config_path):
            # Create default config
            self._create_default_config()
        
        with open(self.config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        
        # Override with environment variables
        config_data = self._override_with_env(config_data)
        
        # Validate and create config object
        self.config = Config(**config_data)
        
        # Generate config hash for security
        self.config_hash = self._generate_config_hash()
        
        print(f"Configuration loaded successfully")
        print(f"Config hash: {self.config_hash}")
        
        return self.config
    
    def _create_default_config(self):
        """Create a default configuration file."""
        default_config = {
            "blockchain": {
                "chain_id": 8453,
                "rpc_url": "https://base-mainnet.g.alchemy.com/v2/YOUR_API_KEY",
                "wallet_address": "0xca63eB7BcD121FE5B0B74960D7F940f58344ABf7"
            },
            "hedging": {
                "delta_threshold": 50.0,
                "rebalance_window": 30,
                "max_slippage": 0.5
            },
            "risk": {
                "max_leverage": 8.0,
                "funding_cap_apr": 12.0,
                "impermanent_loss_cap": 20.0
            },
            "dashboard": {
                "host": "0.0.0.0",
                "port": 8000,
                "refresh_interval": 15
            },
            "hyperliquid": {
                "api_key": "YOUR_HYPERLIQUID_API_KEY",
                "api_secret": "YOUR_HYPERLIQUID_API_SECRET",
                "testnet": False
            },
            "alerts": {
                "telegram_token": None,
                "telegram_chat_id": None,
                "slack_token": None,
                "slack_channel": None
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
        
        print(f"Created default config file: {self.config_path}")
        print("Please update the configuration with your API keys and settings.")
    
    def _override_with_env(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override config values with environment variables."""
        # Blockchain config
        if os.getenv("BLOCKCHAIN_RPC_URL"):
            config_data["blockchain"]["rpc_url"] = os.getenv("BLOCKCHAIN_RPC_URL")
        if os.getenv("BLOCKCHAIN_WALLET_ADDRESS"):
            config_data["blockchain"]["wallet_address"] = os.getenv("BLOCKCHAIN_WALLET_ADDRESS")
        if os.getenv("BLOCKCHAIN_PRIVATE_KEY"):
            config_data["blockchain"]["private_key"] = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
        
        # Hyperliquid config
        if os.getenv("HYPERLIQUID_API_KEY"):
            config_data["hyperliquid"]["api_key"] = os.getenv("HYPERLIQUID_API_KEY")
        if os.getenv("HYPERLIQUID_API_SECRET"):
            config_data["hyperliquid"]["api_secret"] = os.getenv("HYPERLIQUID_API_SECRET")
        
        # Alert config
        if os.getenv("TELEGRAM_TOKEN"):
            config_data["alerts"]["telegram_token"] = os.getenv("TELEGRAM_TOKEN")
        if os.getenv("TELEGRAM_CHAT_ID"):
            config_data["alerts"]["telegram_chat_id"] = os.getenv("TELEGRAM_CHAT_ID")
        if os.getenv("SLACK_TOKEN"):
            config_data["alerts"]["slack_token"] = os.getenv("SLACK_TOKEN")
        if os.getenv("SLACK_CHANNEL"):
            config_data["alerts"]["slack_channel"] = os.getenv("SLACK_CHANNEL")
        
        return config_data
    
    def _generate_config_hash(self) -> str:
        """Generate a hash of the configuration for security verification."""
        config_str = yaml.dump(self.config.dict(), default_flow_style=False, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
    
    def get_config(self) -> Config:
        """Get the loaded configuration."""
        if self.config is None:
            return self.load_config()
        return self.config
    
    def reload_config(self) -> Config:
        """Reload configuration from file."""
        self.config = None
        return self.load_config()

# Global config instance
config_loader = ConfigLoader() 