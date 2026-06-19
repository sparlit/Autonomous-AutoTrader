import importlib
import os
import logging
from typing import Dict, Type, Optional
from src.python.brains.base import BaseBrain

logger = logging.getLogger("AAT_BrainRegistry")

class BrainRegistry:
    def __init__(self, strategy_dir: str = "src/python/brains/strategies"):
        """
        Initialize a BrainRegistry instance.
        
        Parameters:
            strategy_dir (str): Directory path containing strategy modules to be loaded.
                Defaults to "src/python/brains/strategies".
        """
        self.strategy_dir = strategy_dir
        self.strategies: Dict[str, BaseBrain] = {}

    def load_strategies(self):
        """
        Discover and instantiate strategy classes from the configured directory.
        
        Scans the strategy directory for Python modules and registers any BaseBrain
        subclasses found by module name. Creates the directory if it does not exist.
        """
        if not os.path.exists(self.strategy_dir):
            os.makedirs(self.strategy_dir)

        for filename in os.listdir(self.strategy_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"src.python.brains.strategies.{module_name}")
                    # Find classes that inherit from BaseBrain
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseBrain) and attr != BaseBrain:
                            self.strategies[module_name] = attr()
                            logger.info(f"Loaded strategy: {module_name}")
                except Exception as e:
                    logger.error(f"Failed to load strategy {module_name}: {e}")

    def get_strategy(self, name: str) -> Optional[BaseBrain]:
        """
        Retrieve a registered strategy by name.
        
        Returns:
            A `BaseBrain` instance if the strategy is registered, `None` otherwise.
        """
        return self.strategies.get(name)
