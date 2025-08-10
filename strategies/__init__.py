"""
Strategy module initialization
Last updated: 2025-08-10 04:19:31
User: Kish19691969
"""

from .strategy_base import StrategyBase, TradeSignal, SignalType
from .strategy_manager import StrategyManager
from .strategy2 import Strategy2  # Adding Strategy2 import

__all__ = [
    'StrategyBase',
    'TradeSignal',
    'SignalType',
    'StrategyManager',
    'Strategy2'  # Making Strategy2 available for import
]

# Module configuration
__version__ = '1.0.0'
__author__ = 'Kish19691969'
__last_updated__ = '2025-08-10 04:19:31'