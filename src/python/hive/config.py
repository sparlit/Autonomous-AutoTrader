from pydantic import BaseModel, Field
from typing import Dict, Optional
import json
import os

class InstitutionalSettings(BaseModel):
    """V4.0: Hardened Institutional Settings."""
    version: str = "4.0.0-PRO"
    standard_lot_size: float = 0.01
    allow_user_override: bool = True
    max_drawdown_limit: float = 5.0
    min_profit_scaling_usd: float = 1.0
    profit_lock_threshold_rr: float = 1.0
    breakeven_buffer_usd: float = 0.10

class BridgeConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8008
    dashboard_port: int = 8009

class RiskConfig(BaseModel):
    daily_loss_limit_pct: float = 2.0
    max_drawdown_pct: float = 5.0
    min_lot_size: float = 0.01

class SystemConfig(BaseModel):
    global_magic: int = 123456
    database_path: str = "audit_records.db"

class AATConfig(BaseModel):
    bridge: BridgeConfig = Field(default_factory=BridgeConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    institutional: InstitutionalSettings = Field(default_factory=InstitutionalSettings)

def load_config(path: str = "config/main_config.json") -> AATConfig:
    config = AATConfig()
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            config = AATConfig(**data)

    # Overlay institutional settings from its own hardened file
    inst_path = "config/institutional_settings.json"
    if os.path.exists(inst_path):
        with open(inst_path, "r") as f:
            inst_data = json.load(f)
            config.institutional = InstitutionalSettings(**inst_data)

    return config

def save_institutional_settings(settings: InstitutionalSettings, path: str = "config/institutional_settings.json"):
    with open(path, "w") as f:
        json.dump(settings.dict(), f, indent=4)
