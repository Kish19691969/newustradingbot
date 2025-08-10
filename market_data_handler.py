from ib_insync import IB, Stock, util
import pandas as pd
import asyncio
from pathlib import Path
import logging
from datetime import datetime, timezone
import numpy as np
from collections import defaultdict
import talib
from PyQt5.QtCore import QDateTime

class MarketDataHandler:
    def __init__(self, client_id=199):
        self.ib = IB()
        self.client_id = client_id
        self.ticker_data = {}
        self.live_data = defaultdict(dict)
        self.timeframes = [1, 2, 5, 15, 60]  # minutes
        self.ema_periods = [8, 21, 50]
        self.ticker_list = []
        self.dashboard_logger = None
        self.live_bars = {}  # Store live bar data
        self.subscribed_symbols = set()
        self.user_login = "Kish19691969"  # Initialize user_login attribute

        # Separate ATR related data
        self.atr_data = defaultdict(dict)
        self.atr_period = 14
        self.logger = self._setup_logger()


        # Define bar size mapping
        self.bar_size_map = {
            1: "1 min",
            2: "2 mins",
            3: "3 mins",
            5: "5 mins",
            10: "10 mins",
            15: "15 mins",
            20: "20 mins",
            30: "30 mins",
            60: "1 hour",
            120: "2 hours",
            180: "3 hours",
            240: "4 hours",
            480: "8 hours",
        }


    @property
    def user_login(self):
        return self._user_login

    @user_login.setter
    def user_login(self, value):
        self._user_login = value


    def log_to_dashboard(self, message, level="INFO"):
        """
        Send formatted log message to dashboard
        Args:
            message: The message to log
            level: The log level (INFO, ERROR, WARNING)
        """
        if self.dashboard_logger:
            formatted_message = (
                f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')}\n"
                f"Current User's Login: {self.user_login}\n"
                f"Level: {level}\n"
                f"Message: {message}"
            )
            self.dashboard_logger(formatted_message)

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
            self.log_to_dashboard(f"Connected to IB on port {port} with client ID {self.client_id}")

            # Verify connection
            if self.ib.isConnected():
                account = self.ib.managedAccounts()[0] if self.ib.managedAccounts() else None
                self.log_to_dashboard(f"Successfully connected. Account: {account}")
            else:
                raise ConnectionError("Failed to establish IB connection")

        except Exception as e:
            self.log_to_dashboard(f"Failed to connect to IB: {e}")
            raise

    def load_tickers(self):
        """Load ticker list and create Stock objects"""
        try:
            self.log_to_dashboard("Starting to load ticker list...", "INFO")

            # Read the existing ticker file
            with open('c:/trading/US_ticker_list_for_trading.txt', 'r') as f:
                # Read and clean the symbols
                symbols = []
                for line in f:
                    symbol = line.strip()
                    if symbol and not symbol.startswith('#'):  # Skip empty lines and comments
                        symbols.append(symbol)

            if not symbols:
                self.log_to_dashboard("Warning: No valid symbols found in ticker file", "WARNING")
                return

            # Create Stock objects
            self.ticker_list = []
            for symbol in symbols:
                try:
                    stock = Stock(symbol, 'SMART', 'USD')
                    self.ticker_list.append(stock)
                except Exception as e:
                    self.log_to_dashboard(f"Error creating Stock object for {symbol}: {str(e)}", "WARNING")
                    continue

            self.log_to_dashboard(f"Successfully loaded {len(self.ticker_list)} tickers", "INFO")

            # Log the actual tickers loaded
            ticker_names = [stock.symbol for stock in self.ticker_list]
            self.log_to_dashboard(f"Loaded tickers: {', '.join(ticker_names)}", "INFO")

        except Exception as e:
            self.log_to_dashboard(f"Error loading ticker list: {str(e)}", "ERROR")
            raise

        if not self.ticker_list:
            raise Exception("No valid tickers were loaded")


    def get_bar_size(self, mins):
        """Convert timeframe in minutes to IB bar size format"""
        if mins not in self.bar_size_map:
            self.log_to_dashboard(f"Invalid timeframe: {mins} minutes. Using 1 min as default.", "WARNING")
            return "1 min"
        return self.bar_size_map[mins]


    async def fetch_market_data(self, symbol):
        """Fetch historical market data for a single symbol across all timeframes"""
        try:
            # Create the Stock object directly from the symbol string
            if isinstance(symbol, Stock):
                contract = symbol
            else:
                contract = Stock(symbol, 'SMART', 'USD')

            self.log_to_dashboard(f"Requesting market data for {contract.symbol}", "INFO")

            qualified = await self.ib.qualifyContractsAsync(contract)
            if not qualified:
                self.log_to_dashboard(f"Could not qualify contract for {contract.symbol}", "ERROR")
                return


            self.ticker_data[symbol] = {}
            for timeframe in self.timeframes:
                try:
                    bar_size = self.get_bar_size(timeframe)
                    self.log_to_dashboard(f"Requesting {bar_size} data for {contract.symbol}", "INFO")

                    bars = await self.ib.reqHistoricalDataAsync(
                        qualified[0],
                        endDateTime='',
                        durationStr='2 D',
                        barSizeSetting=bar_size,
                        whatToShow='TRADES',
                        useRTH=True
                    )

                    if bars:
                        df = util.df(bars)
                        # Calculate EMAs
                        for period in self.ema_periods:
                            df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

                        self.ticker_data[contract.symbol][timeframe] = df
                        self.log_to_dashboard(f"Fetched {bar_size} data for {contract.symbol}", "INFO")
                    else:
                        self.log_to_dashboard(f"No data received for {contract.symbol} at {bar_size}", "WARNING")

                except Exception as e:
                    self.log_to_dashboard(f"Error fetching {timeframe}min data for {contract.symbol}: {str(e)}", "ERROR")
                    continue

            return self.ticker_data[symbol]

        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    async def fetch_all_market_data(self):
        """Fetch historical market data for all symbols concurrently"""
        try:
            self.log_to_dashboard("Starting to fetch market data for all symbols", "INFO")
            tasks = []
            for stock in self.ticker_list:
                if isinstance(stock, str):
                    symbol = stock
                else:
                    symbol = stock.symbol
                tasks.append(self.fetch_market_data(symbol))

            await asyncio.gather(*tasks)
            self.log_to_dashboard("Completed fetching market data for all symbols", "INFO")
        except Exception as e:
            self.log_to_dashboard(f"Error in fetch_all_market_data: {e}", "ERROR")
            raise

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
            self.log_to_dashboard(f"Error updating EMAs for {symbol}: {e}", "ERROR")

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
            self.log_to_dashboard(f"Error calculating ATR ratio for {symbol}: {e}", "ERROR")
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

            # Update EMAs and other calculations
            self.update_emas(symbol, timeframe)
            atr_ratio = self.calculate_atr_ratio(symbol) if timeframe == 1 else None

            # Prepare data package for strategy processing
            data = {
                'symbol': symbol,
                'timeframe': timeframe,
                'bar_data': {
                    **bar_dict,
                    **self.live_data[symbol][timeframe],  # This includes EMAs
                    'atr_ratio': atr_ratio
                }
            }

            # Emit the data to any registered callbacks
            if hasattr(self, 'data_callback') and self.data_callback:
                self.data_callback(data)

        except Exception as e:
            self.log_to_dashboard(f"Error in bar update for {symbol}: {str(e)}", "ERROR")

    async def start_realtime_data(self, symbol):
        """Start real-time data subscription for a symbol"""
        try:
            # Get symbol string if input is a Stock object
            symbol_str = symbol.symbol if isinstance(symbol, Stock) else symbol

            if symbol_str in self.subscribed_symbols:
                self.log_to_dashboard(f"Already subscribed to {symbol_str}", "INFO")
                return

            # Create a new Stock contract
            contract = Stock(symbol_str, 'SMART', 'USD')

            qualified = await self.ib.qualifyContractsAsync(contract)
            if not qualified:
                self.log_to_dashboard(f"Could not qualify contract for {symbol_str}", "ERROR")
                return

            # Subscribe to real-time bars for each timeframe
            for timeframe in self.timeframes:
                bar_size = self.get_bar_size(timeframe)
                key = f"{symbol_str}_{timeframe}"
                self.live_bars[key] = []

                self.log_to_dashboard(f"Requesting real-time {bar_size} bars for {symbol_str}", "INFO")

                bars = self.ib.reqRealTimeBars(
                    qualified[0],
                    5,  # Bar period in seconds
                    'TRADES',
                    useRTH=True
                )
                bars.updateEvent += lambda bar, s=symbol_str, tf=timeframe: self.on_bar_update(bar, s, tf)

            self.subscribed_symbols.add(symbol_str)
            self.log_to_dashboard(f"Successfully subscribed to {symbol_str}", "INFO")

        except Exception as e:
            self.log_to_dashboard(f"Error starting real-time data for {symbol}: {str(e)}", "ERROR")
            raise

    async def start_all_realtime_data(self):
        """Start real-time data for all symbols"""
        try:
            self.log_to_dashboard("Starting real-time data subscriptions for all symbols", "INFO")
            for stock in self.ticker_list:
                symbol = stock.symbol if isinstance(stock, Stock) else stock
                await self.start_realtime_data(symbol)
        except Exception as e:
            self.log_to_dashboard(f"Error starting all real-time data: {str(e)}", "ERROR")
            raise

    async def stop_realtime_data(self, symbol):
        """Stop real-time data subscription for a symbol"""
        try:
            # Get symbol string if input is a Stock object
            symbol_str = symbol.symbol if isinstance(symbol, Stock) else symbol

            if symbol_str not in self.subscribed_symbols:
                self.log_to_dashboard(f"Not subscribed to {symbol_str}", "INFO")
                return

            contract = Stock(symbol_str, 'SMART', 'USD')
            qualified = await self.ib.qualifyContractsAsync(contract)
            if qualified:
                self.ib.cancelRealTimeBars(qualified[0])

            # Clean up stored data
            self.subscribed_symbols.remove(symbol_str)
            for timeframe in self.timeframes:
                key = f"{symbol_str}_{timeframe}"
                if key in self.live_bars:
                    del self.live_bars[key]
                if symbol_str in self.live_data and timeframe in self.live_data[symbol_str]:
                    del self.live_data[symbol_str][timeframe]

            self.log_to_dashboard(f"Stopped real-time data subscription for {symbol_str}", "INFO")

        except Exception as e:
            self.log_to_dashboard(f"Error stopping real-time data for {symbol}: {str(e)}", "ERROR")
            raise

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