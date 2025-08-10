from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass
from .strategy_base import StrategyBase, TradeSignal, SignalType


@dataclass
class Strategy2Position:
    symbol: str
    entry_price: float
    entry_time: datetime
    entry_candle_low: float
    position_size: float
    remaining_size: float  # Track remaining position after partial sells
    initial_stop_loss: float
    take_profit_level: float


class Strategy2(StrategyBase):
    def __init__(self, dashboard, market_data, config):
        super().__init__(dashboard, market_data, config)
        self.name = "Strategy2_EMA_ATR"
        self.positions: Dict[str, Strategy2Position] = {}
        self.timeframes = {
            'daily': 'D',
            '5min': '5'
        }
        self.ema_periods = [8, 21, 50]
        self.atr_ratio_threshold = 5
        self.partial_sell_percentage = 0.75
        self.last_update = "2025-08-10 04:10:30"
        self.user_login = "Kish19691969"

    def check_override_conditions(self, symbol: str, data: Dict) -> bool:
        """Check daily timeframe EMA alignment"""
        daily_data = self.market_data.get_timeframe_data(symbol, 'D')
        if daily_data is None or len(daily_data) < 50:
            return False

        price = daily_data['close'].iloc[-1]
        ema8 = daily_data['EMA_8'].iloc[-1]
        ema21 = daily_data['EMA_21'].iloc[-1]
        ema50 = daily_data['EMA_50'].iloc[-1]

        # Check EMA alignment: price > EMA8 > EMA21 > EMA50
        return (price > ema8 > ema21 > ema50)

    def generate_signals(self, data: Dict) -> List[TradeSignal]:
        signals = []

        for symbol, symbol_data in data.items():
            # Skip if position exists
            if self._has_existing_position(symbol):
                self._check_exit_signals(symbol, symbol_data, signals)
                continue

            # Check buy conditions
            if self._check_buy_conditions(symbol, symbol_data):
                signals.append(self._create_buy_signal(symbol, symbol_data))

        return signals

    def _check_buy_conditions(self, symbol: str, data: Dict) -> bool:
        """Check all buy conditions"""
        # Get 5-minute data
        five_min_data = self.market_data.get_timeframe_data(symbol, '5')
        if five_min_data is None or len(five_min_data) < 50:
            return False

        # Check override conditions first
        if not self.check_override_conditions(symbol, data):
            return False

        # Check 50 EMA cross on 5-min
        current_price = five_min_data['close'].iloc[-1]
        previous_close = five_min_data['close'].iloc[-2]
        current_ema50 = five_min_data['EMA_50'].iloc[-1]
        previous_ema50 = five_min_data['EMA_50'].iloc[-2]

        return (previous_close <= previous_ema50 and
                current_price > current_ema50)

    def _check_exit_signals(self, symbol: str, data: Dict, signals: List[TradeSignal]):
        """Check all exit conditions"""
        position = self.positions.get(symbol)
        if not position:
            return

        five_min_data = self.market_data.get_timeframe_data(symbol, '5')
        if five_min_data is None:
            return

        current_price = five_min_data['close'].iloc[-1]
        atr_ratio = self.market_data.get_atr_ratio(symbol)

        # Check exit conditions
        # 1. ATR ratio threshold (partial exit)
        if (atr_ratio >= self.atr_ratio_threshold and
                position.remaining_size == position.position_size):
            signals.append(self._create_sell_signal(
                symbol,
                current_price,
                "ATR Ratio Exit",
                self.partial_sell_percentage
            ))

        # 2. Price below 50 EMA
        current_ema50 = five_min_data['EMA_50'].iloc[-1]
        if current_price < current_ema50:
            signals.append(self._create_sell_signal(
                symbol,
                current_price,
                "EMA Cross Exit",
                1.0
            ))

        # 3. Take profit
        if current_price >= position.take_profit_level:
            signals.append(self._create_sell_signal(
                symbol,
                current_price,
                "Take Profit",
                1.0
            ))

        # 4. Stop loss
        if (current_price <= position.initial_stop_loss or
                current_price < position.entry_candle_low):
            signals.append(self._create_sell_signal(
                symbol,
                current_price,
                "Stop Loss",
                1.0
            ))

    def _create_buy_signal(self, symbol: str, data: Dict) -> TradeSignal:
        """Create a buy signal with calculated levels"""
        current_price = data['close'].iloc[-1]

        return TradeSignal(
            symbol=symbol,
            signal_type=SignalType.BUY,
            price=current_price,
            timestamp="2025-08-10 04:10:30",
            strategy_name=self.name,
            additional_info={
                'entry_candle_low': data['low'].iloc[-1],
                'stop_loss': current_price * (1 - self.config.stop_loss_percentage),
                'take_profit': current_price * (1 + self.config.take_profit_percentage)
            }
        )

    def _create_sell_signal(
            self,
            symbol: str,
            price: float,
            reason: str,
            sell_percentage: float
    ) -> TradeSignal:
        """Create a sell signal"""
        position = self.positions[symbol]
        sell_size = position.remaining_size * sell_percentage

        return TradeSignal(
            symbol=symbol,
            signal_type=SignalType.SELL,
            price=price,
            timestamp="2025-08-10 04:10:30",
            strategy_name=self.name,
            additional_info={
                'reason': reason,
                'sell_size': sell_size,
                'remaining_size': position.remaining_size - sell_size,
                'entry_price': position.entry_price
            }
        )