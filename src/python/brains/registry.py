import os
import importlib
import logging
from typing import Dict, Optional, List
from src.python.brains.base import BaseBrain

class BrainRegistry:
    def __init__(self, strategy_dir: str = "src/python/brains/strategies"):
        """Magic: 13001"""
        self.strategies: Dict[str, BaseBrain] = {}
        self.strategy_dir = strategy_dir
        self.load_strategies()

    def load_strategies(self):
        """Magic: 13002"""
        if not os.path.exists(self.strategy_dir):
            logging.error(f"Registry: Path {self.strategy_dir} not found.")
            return

        for file in os.listdir(self.strategy_dir):
            if file.endswith(".py") and file != "__init__.py":
                module_name = f"src.python.brains.strategies.{file[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseBrain) and attr is not BaseBrain:
                            # Unique name instantiation
                            strategy_instance = attr(attr_name)
                            self.strategies[attr_name] = strategy_instance
                            logging.info(f"Registry: Loaded strategy {attr_name} [Magic: {getattr(strategy_instance, 'magic', 0)}]")
                except Exception as e:
                    logging.error(f"Registry: Failed to load {module_name}: {e}")

    def get_strategy(self, name: str) -> Optional[BaseBrain]:
        """Magic: 13003"""
        return self.strategies.get(name)
