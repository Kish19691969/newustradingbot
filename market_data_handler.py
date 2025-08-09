from ib_insync import *
import pandas as pd
import asyncio
from pathlib import Path
import logging
from datetime import datetime, timezone
import numpy as np
from collections import defaultdict
import talib


class MarketDataHandler:
    def __init__(self, client_id=199):
        self.ib = IB()
        self.client_id = client_id
        self.ticker_data = {}
        self.live_data = defaultdict(dict)
        self.timeframes = [1, 2, 5, 15, 50]  # minutes
        self.ema_periods = [8, 21, 50]
        self.ticker_list = []
        self.logger = self._setup_logger()
        self.live_bars = {}  # Store live bar data
        self.subscribed_symbols = set()

        # Separate ATR related data
        self.atr_data = defaultdict(dict)
        self.atr_period = 14

    def _setup_logger(self):
        """Set up logging configuration"""
        logger = logging.getLogger('MarketDataHandler')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def connect_ib(self, port=7496, host='127.0.0.1'):
        """Connect to IB TWS/Gateway"""
        try:
            await self.ib.connectAsync(host=host, port=port, clientId=self.client_id)
            self.logger.info(f"Connected to IB on port {port} with client ID {self.client_id}")

            # Verify connection
            if self.ib.isConnected():
                account = self.ib.managedAccounts()[0] if self.ib.managedAccounts() else None
                self.logger.info(f"Successfully connected. Account: {account}")
            else:
                raise ConnectionError("Failed to establish IB connection")

        except Exception as e:
            self.logger.error(f"Failed to connect to IB: {e}")
            raise

    def load_tickers(self):
        """Load ticker list from file"""
        try:
            ticker_path = Path(r'c:\trading\US_ticker_list_for_trading')
            self.ticker_list = pd.read_csv(ticker_path, header=None)[0].tolist()
            self.logger.info(f"Loaded {len(self.ticker_list)} tickers")
        except Exception as e:
            self.logger.error(f"Error loading ticker list: {e}")
            raise

    async def fetch_market_data(self, symbol):
        """Fetch historical market data for a single symbol across all timeframes"""
        contract = Stock(symbol, 'SMART', 'USD')
        try:
            qualified = await self.ib.qualifyContractsAsync(contract)
            if not qualified:
                self.logger.error(f"Could not qualify contract for {symbol}")
                return

            self.ticker_data[symbol] = {}
            for timeframe in self.timeframes:
                bars = await self.ib.reqHistoricalDataAsync(
                    qualified[0],
                    endDateTime='',
                    durationStr='2 D',
                    barSizeSetting=f'{timeframe} mins',
                    whatToShow='TRADES',
                    useRTH=True
                )

                if bars:
                    df = util.df(bars)
                    # Calculate EMAs
                    for period in self.ema_periods:
                        df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

                    self.ticker_data[symbol][timeframe] = df
                    self.logger.info(f"Fetched {timeframe}min data for {symbol}")

            return self.ticker_data[symbol]

        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    async def fetch_all_market_data(self):
        """Fetch historical market data for all symbols concurrently"""
        tasks = [self.fetch_market_data(symbol) for symbol in self.ticker_list]
        await asyncio.gather(*tasks)

    def update_emas(self, symbol, timeframe):
        """Calculate EMAs based on latest data"""
        try:
            key = f"{symbol}_{timeframe}"
            if not self.live_bars[key]:
                return

            # Convert to DataFrame
            df = pd.DataFrame(self.live_bars[key])

            # Calculate EMAs
            for period in self.ema_periods:
                ema_key = f'EMA_{period}'
                df[ema_key] = df['close'].ewm(span=period, adjust=False).mean()

            # Store latest values
            latest = df.iloc[-1].to_dict()
            self.live_data[symbol][timeframe] = latest

        except Exception as e:
            self.logger.error(f"Error updating EMAs for {symbol}: {e}")

    def calculate_atr_ratio(self, symbol):
        """Calculate ATR and ATR ratio for 1-minute timeframe"""
        try:
            key = f"{symbol}_1"  # Only for 1-minute timeframe
            if key not in self.live_bars or not self.live_bars[key]:
                return None

            df = pd.DataFrame(self.live_bars[key])

            # Calculate ATR
            df['ATR'] = talib.ATR(
                df['high'].values,
                df['low'].values,
                df['close'].values,
                timeperiod=self.atr_period
            )

            # Get latest EMA_50 from live data
            ema_50 = self.live_data[symbol][1].get('EMA_50')
            if ema_50 is None:
                return None

            # Calculate ATR ratio
            latest_close = df['close'].iloc[-1]
            latest_atr = df['ATR'].iloc[-1]

            if latest_atr != 0:  # Prevent division by zero
                atr_ratio = (latest_close - ema_50) / latest_atr

                # Store in separate ATR data structure
                self.atr_data[symbol] = {
                    'timestamp': df.index[-1],
                    'ATR': latest_atr,
                    'ATR_ratio': atr_ratio
                }

                return atr_ratio

            return None

        except Exception as e:
            self.logger.error(f"Error calculating ATR ratio for {symbol}: {e}")
            return None

    def get_latest_atr_data(self, symbol):
        """Get the latest ATR data for a symbol"""
        return self.atr_data.get(symbol)

    def on_bar_update(self, bar, symbol, timeframe):
        """Handle real-time bar updates"""
        try:
            bar_dict = {
                'date': bar.time,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume
            }

            # Add to live bars
            key = f"{symbol}_{timeframe}"
            self.live_bars[key].append(bar_dict)

            # Keep only necessary bars for EMA calculation
            max_lookback = max(max(self.ema_periods), self.atr_period) * 2
            if len(self.live_bars[key]) > max_lookback:
                self.live_bars[key] = self.live_bars[key][-max_lookback:]

            # Update EMAs
            self.update_emas(symbol, timeframe)

        except Exception as e:
            self.logger.error(f"Error in bar update for {symbol}: {e}")

    async def start_realtime_data(self, symbol):
        """Start real-time data subscription for a symbol"""
        if symbol in self.subscribed_symbols:
            return

        contract = Stock(symbol, 'SMART', 'USD')
        qualified = await self.ib.qualifyContractsAsync(contract)

        if not qualified:
            self.logger.error(f"Could not qualify contract for {symbol}")
            return

        # Subscribe to real-time bars for each timeframe
        for timeframe in self.timeframes:
            self.live_bars[f"{symbol}_{timeframe}"] = []

            bars = self.ib.reqRealTimeBars(
                qualified[0],
                barSize=timeframe,
                whatToShow='TRADES',
                useRTH=True
            )
            bars.updateEvent += lambda bar, symbol=symbol, tf=timeframe: self.on_bar_update(bar, symbol, tf)

        self.subscribed_symbols.add(symbol)
        self.logger.info(f"Started real-time data subscription for {symbol}")

    async def start_all_realtime_data(self):
        """Start real-time data for all symbols"""
        for symbol in self.ticker_list:
            await self.start_realtime_data(symbol)

    async def stop_realtime_data(self, symbol):
        """Stop real-time data subscription for a symbol"""
        if symbol not in self.subscribed_symbols:
            return

        try:
            contract = Stock(symbol, 'SMART', 'USD')
            qualified = await self.ib.qualifyContractsAsync(contract)
            if qualified:
                self.ib.cancelRealTimeBars(qualified[0])

            self.subscribed_symbols.remove(symbol)
            # Clean up stored data
            for timeframe in self.timeframes:
                key = f"{symbol}_{timeframe}"
                if key in self.live_bars:
                    del self.live_bars[key]
                if symbol in self.live_data:
                    if timeframe in self.live_data[symbol]:
                        del self.live_data[symbol][timeframe]

            self.logger.info(f"Stopped real-time data subscription for {symbol}")

        except Exception as e:
            self.logger.error(f"Error stopping real-time data for {symbol}: {e}")

    async def stop_all_realtime_data(self):
        """Stop all real-time data subscriptions"""
        for symbol in list(self.subscribed_symbols):
            await self.stop_realtime_data(symbol)

    def get_latest_live_data(self, symbol, timeframe):
        """Get the latest real-time data including EMAs"""
        try:
            return self.live_data[symbol][timeframe]
        except KeyError:
            self.logger.error(f"No live data available for {symbol} at {timeframe}min timeframe")
            return None

    async def disconnect(self):
        """Safely disconnect from IB"""
        try:
            await self.stop_all_realtime_data()
            self.ib.disconnect()
            self.logger.info("Disconnected from IB")
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")

    async def start(self):
        """Initialize everything"""
        await self.connect_ib()
        self.load_tickers()
        await self.fetch_all_market_data()