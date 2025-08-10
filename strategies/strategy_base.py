from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    SELL_SHORT = "SELL_SHORT"
    BUY_TO_COVER = "BUY_TO_COVER"
    HOLD = "HOLD"
    EXIT = "EXIT"

@dataclass
class TradeSignal:
    symbol: str
    signal_type: SignalType
    price: float
    quantity: int = 0
    timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    strategy_name: str = ""
    additional_info: Dict = None

class StrategyBase(ABC):
    def __init__(self, dashboard, market_data, config):
        self.dashboard = dashboard
        self.market_data = market_data
        self.config = config
        self.name = self.__class__.__name__
        
        # Trading parameters
        self.max_position_dollars = 5000.0
        self.profit_target_percent = 3.0
        self.stop_loss_percent = 2.0
        self.max_trades_per_day = 5
        
        # Strategy state
        self.current_positions = {}
        self.today_trade_count = 0
        self.last_update_time = None
        self.user_login = "Kish19691969"

    @abstractmethod
    def generate_signals(self, data: Dict) -> List[TradeSignal]:
        """Each strategy must implement this method to generate trading signals"""
        pass

    def check_global_conditions(self, signal: TradeSignal) -> bool:
        """Check if global trading conditions are met"""
        # Check if we've exceeded max trades for the day
        if self.today_trade_count >= self.max_trades_per_day:
            return False
            
        # Check if we have an existing position for non-exit signals
        if signal.signal_type not in [SignalType.EXIT, SignalType.SELL, SignalType.BUY_TO_COVER]:
            if signal.symbol in self.current_positions:
                return False
                
        return True

    def update_state(self):
        """Update strategy state (e.g., reset daily counters)"""
        current_time = datetime.now()
        
        # Reset daily counters if it's a new trading day
        if self.last_update_time and self.last_update_time.date() != current_time.date():
            self.today_trade_count = 0
            
        self.last_update_time = current_time

    def calculate_position_size(self, price: float) -> int:
        """Calculate the number of shares to trade based on max position size"""
        if price <= 0:
            return 0
        shares = int(self.max_position_dollars / price)
        return shares

    def calculate_profit_target(self, entry_price: float) -> float:
        """Calculate the profit target price"""
        return entry_price * (1 + self.profit_target_percent / 100)

    def calculate_stop_loss(self, entry_price: float) -> float:
        """Calculate the stop loss price"""
        return entry_price * (1 - self.stop_loss_percent / 100)

    def validate_signal(self, signal: TradeSignal) -> bool:
        """Validate a trading signal"""
        if not signal.symbol or not isinstance(signal.signal_type, SignalType):
            return False
            
        if signal.price <= 0:
            return False
            
        # Set quantity if not already set
        if signal.quantity <= 0:
            signal.quantity = self.calculate_position_size(signal.price)
            
        return True

    def process_market_data(self, market_data: Dict) -> None:
        """Process incoming market data and update strategy state"""
        self.market_data.update(market_data)
        self.update_state()

    def manage_positions(self):
        """Manage existing positions (check stops, targets, etc.)"""
        signals = []
        
        for symbol, position in self.current_positions.items():
            current_price = self.market_data.get(symbol, {}).get('price')
            if not current_price:
                continue
                
            # Check stop loss
            if current_price <= position['stop_loss']:
                signals.append(TradeSignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    price=current_price,
                    quantity=position['quantity']
                ))
                
            # Check profit target
            elif current_price >= position['profit_target']:
                signals.append(TradeSignal(
                    symbol=symbol,
                    signal_type=SignalType.EXIT,
                    price=current_price,
                    quantity=position['quantity']
                ))
                
        return signals
