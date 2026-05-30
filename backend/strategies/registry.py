import importlib
import inspect
import os
from typing import List, Type
from backend.strategies.base import BaseStrategy

class StrategyRegistry:
    @staticmethod
    def get_active_strategies() -> List[BaseStrategy]:
        """
        Dynamically load strategies from the strategies directory.
        For now, we'll return instances of all found BaseStrategy subclasses.
        In a real scenario, this would filter by ENABLED_STRATEGIES env var.
        """
        strategies = []
        strategy_dir = os.path.dirname(__file__)
        
        for filename in os.listdir(strategy_dir):
            if filename.endswith(".py") and filename not in ["__init__.py", "base.py", "registry.py"]:
                module_name = f"backend.strategies.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                            strategies.append(obj())
                except Exception as e:
                    print(f"Error loading strategy {module_name}: {e}")
        
        return strategies
