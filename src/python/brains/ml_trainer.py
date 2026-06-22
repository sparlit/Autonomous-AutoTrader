import polars as pl
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import RandomForestRegressor
import logging
from typing import Dict, Any, List

logger = logging.getLogger("AAT_ML")

class PytorchRegimeModel(nn.Module):
    """Magic: 41001"""
    def __init__(self, input_dim=5):
        super(PytorchRegimeModel, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 3),
            nn.Softmax(dim=1)
        )
        self.magic = 41001

    def forward(self, x):
        return self.fc(x)

class MLTrainer:
    """
    Zero-Tolerance Institutional ML Engine.
    Magic: 40001
    """
    def __init__(self):
        self.magic = 40001
        self.regime_model = PytorchRegimeModel()
        self.ranker = RandomForestRegressor(n_estimators=100)
        self.models_ready = False

    def engineer_features(self, df_pandas) -> pl.DataFrame:
        """Magic: 40002 - Polars Accelerated Engineering"""
        df = pl.from_pandas(df_pandas)
        df = df.with_columns([
            (pl.col("c") / pl.col("c").shift(1) - 1).alias("returns"),
            (pl.col("h") - pl.col("l")).alias("range"),
            pl.col("v").rolling_mean(window_size=20).alias("avg_vol")
        ])
        return df.drop_nulls()

    def train_all(self, symbol: str, data_pandas):
        """Magic: 40003"""
        df = self.engineer_features(data_pandas)
        if df.height < 50: return

        X = df.select(["returns", "range", "avg_vol"]).to_numpy()
        y = df.select("returns").to_numpy().flatten()

        self.ranker.fit(X, y)
        self.models_ready = True
        logger.info(f"ML: Trained high-performance models for {symbol}")

    def get_alpha_weight(self, features_np) -> float:
        """Magic: 40004"""
        if not self.models_ready: return 1.0
        return float(self.ranker.predict(features_np.reshape(1, -1))[0])
