from pydantic import BaseModel, Field
from typing import Dict, Optional
import json
import os

class BridgeConfig(BaseModel):
    """13001: Bridge connection settings."""
    host: str = "127.0.0.1"
    port: int = 8008
    dashboard_port: int = 8009
    heartbeat_interval: float = 10.0
    timeout: float = 30.0

class RiskConfig(BaseModel):
    """13002: Risk management thresholds."""
    daily_loss_limit_pct: float = 2.0
    max_drawdown_pct: float = 5.0
    risk_per_trade_pct: float = 1.0
    min_lot_size: float = 0.01

class BrainsConfig(BaseModel):
    """13003: Brain coordination settings."""
    parallel_workers: int = 4
    consensus_threshold: float = 70.0

class AATConfig(BaseModel):
    """13004: Global system configuration."""
    bridge: BridgeConfig = Field(default_factory=BridgeConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    brains: BrainsConfig = Field(default_factory=BrainsConfig)

def load_config(path: str = "config/main_config.json") -> AATConfig:
    """13005: Load and validate JSON configuration."""
    if not os.path.exists(path):
        return AATConfig()
    with open(path, "r") as f:
        data = json.load(f)
        return AATConfig(**data)
