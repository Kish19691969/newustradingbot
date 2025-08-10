from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class TradeSignal:
    symbol: str
    signal_type: SignalType
    price: float
    timestamp: str = "2025-08-10 04:07:51"  # Your current timestamp
    strategy_name: str = ""
    additional_info: Dict = None

class StrategyBase(ABC):
    def __init__(self, dashboard, market_data, config):
        self.dashboard = dashboard
        self.market_data = market_data
        self.config = config
        self.name = self.__class__.__name__
        self.user_login = "Kish19691969"  # Your login

    @abstractmethod
    def generate_signals(self, data: Dict) -> List[TradeSignal]:
        """Each strategy must implement this method"""
        pass

    def check_global_conditions(self, signal: TradeSignal) -> bool:
        """Common conditions that apply to all strategies"""
        return True