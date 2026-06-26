# Version: V3.1.0-AUTONOMOUS (Hardened RESTRUCTURE)
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import json
import os

class SystemConfig(BaseModel):
    global_magic: int = 2026001
    db_path: str = "aat_institutional.db"
    log_level: str = "INFO"

class BridgeConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8008
    web_port: int = 8009

class RiskConfig(BaseModel):
    max_drawdown_pct: float = 5.0
    daily_loss_limit_pct: float = 2.0
    risk_per_trade_pct: float = 1.0
    min_lot_size: float = 0.01

class AATConfig(BaseModel):
    system: SystemConfig = Field(default_factory=SystemConfig)
    bridge: BridgeConfig = Field(default_factory=BridgeConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    symbols: List[str] = ["EURUSD", "GBPUSD", "XAUUSD", "NAS100"]

def load_aat_config(path: str = "config/settings.json") -> AATConfig:
    if os.path.exists(path):
        with open(path, "r") as f:
            return AATConfig(**json.load(f))
    return AATConfig()

def save_aat_config(config: AATConfig, path: str = "config/settings.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(config.dict(), f, indent=4)
