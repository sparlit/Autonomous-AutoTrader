# Version: V3.1.3-AUTONOMOUS (Hardened RESTRUCTURE)
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import json
import os

class SystemConfig(BaseModel):
    global_magic: int = 2026001
    db_path: str = "aat_institutional.db"
    log_level: str = "INFO"
    shm_size_mb: int = 2
    queue_size_kb: int = 1024

class BridgeConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8008
    web_port: int = 8009
    heartbeat_interval: float = 5.0
    reconnect_delay: float = 1.0

class RiskConfig(BaseModel):
    max_drawdown_pct: float = 5.0
    daily_loss_limit_pct: float = 2.0
    risk_per_trade_pct: float = 1.0
    min_lot_size: float = 0.01
    max_spread_pts: float = 50.0

class BrainsConfig(BaseModel):
    tick_rate_ms: int = 5
    consensus_threshold: float = 0.7
    enabled_brains: List[str] = ["SMC_1", "VSA_1", "Meta_1"]

class AATConfig(BaseModel):
    system: SystemConfig = Field(default_factory=SystemConfig)
    bridge: BridgeConfig = Field(default_factory=BridgeConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    brains: BrainsConfig = Field(default_factory=BrainsConfig)
    symbols: List[str] = ["EURUSD", "GBPUSD", "XAUUSD", "NAS100"]

def load_aat_config(path: str = "config/settings.json") -> AATConfig:
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return AATConfig(**json.load(f))
        except: return AATConfig()
    return AATConfig()
