from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime


@dataclass
class TradeSignal:
    symbol: str
    signal_type: str
    timestamp: datetime
    price: float
    quantity: int


class SignalType:
    BUY = "BUY"
    SELL = "SELL"
    SELL_SHORT = "SELL_SHORT"
    BUY_TO_COVER = "BUY_TO_COVER"
    HOLD = "HOLD"
    EXIT = "EXIT"


class StrategyBase:
    def __init__(self, market_data, config):  # Removed dashboard parameter
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

    def generate_signals(self, data: Dict) -> List[TradeSignal]:
        """Generate trading signals based on market data"""
        raise NotImplementedError("Subclasses must implement generate_signals")

    def check_global_conditions(self, signal: TradeSignal) -> bool:
        """Check if global trading conditions are met"""
        # Check if we've exceeded max trades for the day
        if self.today_trade_count >= self.max_trades_per_day:
            return False

        # Check if we have an existing position in this symbol
        if signal.symbol in self.current_positions:
            return False

        # Add more global conditions as needed
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
        if not signal.symbol or not signal.signal_type:
            return False

        if signal.price <= 0 or signal.quantity <= 0:
            return False

        return True