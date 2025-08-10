from typing import Dict, Type
from datetime import datetime
from .strategy_base import StrategyBase, TradeSignal
from market_data_handler import MarketDataHandler

class StrategyManager:
    def __init__(self, dashboard, market_data, config):
        self.dashboard = dashboard
        self.market_data = market_data
        self.config = config
        self.strategies: Dict[str, StrategyBase] = {}
        self.user_login = "Kish19691969"
        self.last_update = "2025-08-10 07:11:20"

    def register_strategy(self, strategy_class: Type[StrategyBase]):
        """Register a new strategy"""
        strategy = strategy_class(self.dashboard, self.market_data, self.config)
        self.strategies[strategy.name] = strategy
        self._log_action(f"Registered strategy: {strategy.name}")

    def process_market_data(self, new_data: Dict):
        """Process new market data through all strategies"""
        for strategy_name, strategy in self.strategies.items():
            try:
                signals = strategy.generate_signals(new_data)
                for signal in signals:
                    if strategy.check_global_conditions(signal):
                        self.dashboard.update_with_signal(signal)
                        if self.config.live_trading_enabled:
                            self._execute_trade(signal)
            except Exception as e:
                self._log_error(f"Error in strategy {strategy_name}: {str(e)}")

    def _execute_trade(self, signal: TradeSignal):
        """Execute trade through IB"""
        # Will implement IB trading logic later
        self._log_action(f"Executing {signal.signal_type} for {signal.symbol}")

    def _log_action(self, message: str):
        """Log manager actions"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dashboard.add_to_system_log(f"{timestamp} - Strategy Manager: {message}")

    def _log_error(self, error_message: str):
        """Log errors"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dashboard.add_to_system_log(f"{timestamp} - ERROR: {error_message}")
