from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                             QGroupBox, QTextEdit, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QColor


class TradingDashboard(QMainWindow):
    def __init__(self, account_id, trading_start, trading_end, max_positions,
                 max_position_dollars, min_stock_price, max_stock_price,
                 strategy_settings):
        super().__init__()

        # Set default fonts
        self.default_font = QFont("Arial", 10)  # Increased base font size
        self.button_font = QFont("Arial", 12, QFont.Bold)  # Larger font for buttons
        self.header_font = QFont("Arial", 14, QFont.Bold)  # Font for section headers

        # Colors for PnL
        self.positive_color = QColor("#006400")  # Dark Green
        self.negative_color = QColor("#8B0000")  # Dark Red

        # Initialize settings first
        self.init_settings(account_id, trading_start, trading_end, max_positions,
                           max_position_dollars, min_stock_price, max_stock_price,
                           strategy_settings)

        # Initialize UI
        self.init_ui()

        # Add all UI components
        self.add_session_info()
        self.create_open_positions_section()
        self.create_trade_log_section()
        self.create_closed_trades_section()
        self.create_strategy_pnl_section()
        self.create_total_pnl_section()
        self.create_system_log_section()
        self.create_control_buttons()

        # Setup timer last
        self.setup_timer()

    def init_settings(self, account_id, trading_start, trading_end, max_positions,
                      max_position_dollars, min_stock_price, max_stock_price,
                      strategy_settings):
        """Initialize all settings passed from the main window"""
        self.account_id = account_id
        self.trading_start = trading_start
        self.trading_end = trading_end
        self.max_positions = max_positions
        self.max_position_dollars = max_position_dollars
        self.min_stock_price = min_stock_price
        self.max_stock_price = max_stock_price
        self.strategy_settings = strategy_settings

    def init_ui(self):
        self.setWindowTitle("Trading App Dashboard")
        self.setMinimumSize(1000, 2000)  # Increased minimum window size

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setSpacing(20)  # Add spacing between sections
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # Add margins around the entire window

    def add_session_info(self):
        info_group = QGroupBox()
        layout = QVBoxLayout()
        layout.setSpacing(10)  # Add space between labels
        layout.setContentsMargins(20, 10, 20, 10)  # Add margins

        # Current date/time with larger font
        self.time_label = QLabel()
        self.time_label.setFont(self.default_font)
        self.time_label.setAlignment(Qt.AlignLeft)
        self.update_time()

        # User login with larger font
        user_label = QLabel("Current User's Login: Kish19691969")
        user_label.setFont(self.default_font)
        user_label.setAlignment(Qt.AlignLeft)

        layout.addWidget(self.time_label)
        layout.addWidget(user_label)

        info_group.setLayout(layout)
        self.main_layout.addWidget(info_group)

    def create_open_positions_section(self):
        group = QGroupBox("Currently Open Positions")
        group.setFont(self.header_font)
        layout = QVBoxLayout()

        self.positions_table = QTableWidget()
        self.positions_table.setFont(self.default_font)
        self.positions_table.setColumnCount(7)
        self.positions_table.setRowCount(5)
        self.positions_table.setMinimumHeight(210)

        headers = ["Time", "Ticker", "Strategy", "Shares", "Entry Price", "Current Price", "Live PnL"]
        self.positions_table.setHorizontalHeaderLabels(headers)

        # Set specific column widths
        self.positions_table.setColumnWidth(0, 200)  # Time
        self.positions_table.setColumnWidth(1, 150)  # Ticker
        self.positions_table.setColumnWidth(2, 300)  # Strategy
        self.positions_table.setColumnWidth(3, 100)  # Shares
        self.positions_table.setColumnWidth(4, 150)  # Entry Price
        self.positions_table.setColumnWidth(5, 150)  # Current Price
        self.positions_table.setColumnWidth(6, 150)  # Live PnL

        # Set row numbers and initial empty rows
        for i in range(5):
            self.positions_table.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
            for j in range(7):
                item = QTableWidgetItem("")
                item.setFont(self.default_font)
                self.positions_table.setItem(i, j, item)

        header = self.positions_table.horizontalHeader()
        header.setFont(self.header_font)
        header.setDefaultAlignment(Qt.AlignLeft)

        layout.addWidget(self.positions_table)
        group.setLayout(layout)
        self.main_layout.addWidget(group)

    def create_trade_log_section(self):
        group = QGroupBox("Trade Log History")
        group.setFont(self.header_font)
        layout = QVBoxLayout()

        self.trade_log_table = QTableWidget()
        self.trade_log_table.setFont(self.default_font)
        self.trade_log_table.setColumnCount(7)
        self.trade_log_table.setRowCount(5)  # Set initial number of rows
        self.trade_log_table.setMinimumHeight(210)  # Increased height for better visibility

        headers = ["Date/Time", "Ticker", "Side", "Price", "Size", "Strategy", "Reason/Notes"]
        self.trade_log_table.setHorizontalHeaderLabels(headers)

        # Set specific column widths
        self.trade_log_table.setColumnWidth(0, 200)  # Date/Time
        self.trade_log_table.setColumnWidth(1, 150)  # Ticker
        self.trade_log_table.setColumnWidth(2, 100)  # Side
        self.trade_log_table.setColumnWidth(3, 100)  # Price
        self.trade_log_table.setColumnWidth(4, 100)  # Size
        self.trade_log_table.setColumnWidth(5, 300)  # Strategy
        self.trade_log_table.setColumnWidth(6, 300)  # Reason/Notes

        # Initialize empty rows
        for i in range(5):
            self.trade_log_table.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
            for j in range(7):
                item = QTableWidgetItem("")
                item.setFont(self.default_font)
                self.trade_log_table.setItem(i, j, item)

        # Style the header
        header = self.trade_log_table.horizontalHeader()
        header.setFont(self.header_font)
        header.setDefaultAlignment(Qt.AlignLeft)
        header.setStretchLastSection(True)

        # Style the table
        self.trade_log_table.setShowGrid(True)
        self.trade_log_table.setAlternatingRowColors(True)
        self.trade_log_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d3d3d3;
                background-color: white;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: 1px solid #d3d3d3;
            }
        """)

        layout.addWidget(self.trade_log_table)
        group.setLayout(layout)
        self.main_layout.addWidget(group)

    def create_closed_trades_section(self):
        group = QGroupBox("Closed / Completed Trades")
        group.setFont(self.header_font)
        layout = QVBoxLayout()

        self.closed_trades_table = QTableWidget()
        self.closed_trades_table.setFont(self.default_font)
        self.closed_trades_table.setColumnCount(3)
        self.closed_trades_table.setRowCount(5)  # Set initial number of rows
        self.closed_trades_table.setMinimumHeight(210)  # Increased height for better visibility

        headers = ["Ticker", "PnL", "Closed Time"]
        self.closed_trades_table.setHorizontalHeaderLabels(headers)

        # Set specific column widths
        self.closed_trades_table.setColumnWidth(0, 150)  # Ticker
        self.closed_trades_table.setColumnWidth(1, 150)  # PnL
        self.closed_trades_table.setColumnWidth(2, 200)  # Closed Time

        # Initialize empty rows
        for i in range(5):
            self.closed_trades_table.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
            for j in range(3):
                item = QTableWidgetItem("")
                item.setFont(self.default_font)
                self.closed_trades_table.setItem(i, j, item)

        # Style the header
        header = self.closed_trades_table.horizontalHeader()
        header.setFont(self.header_font)
        header.setDefaultAlignment(Qt.AlignLeft)
        header.setStretchLastSection(True)

        # Style the table
        self.closed_trades_table.setShowGrid(True)
        self.closed_trades_table.setAlternatingRowColors(True)
        self.closed_trades_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d3d3d3;
                background-color: white;
                alternate-background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: 1px solid #d3d3d3;
            }
        """)

        layout.addWidget(self.closed_trades_table)
        group.setLayout(layout)
        self.main_layout.addWidget(group)


    def create_strategy_pnl_section(self):
        group = QGroupBox("Live PnL by Strategy")
        group.setFont(self.header_font)
        layout = QVBoxLayout()

        self.strategy_pnl_table = QTableWidget()
        strategy_font = QFont("Arial", 14)  # Set base font size for the table
        self.strategy_pnl_table.setFont(strategy_font)
        self.strategy_pnl_table.setColumnCount(2)
        self.strategy_pnl_table.setRowCount(4)

        headers = ["Strategy", "Live Combined Session PnL"]
        self.strategy_pnl_table.setHorizontalHeaderLabels(headers)

        # Set specific column widths
        self.strategy_pnl_table.setColumnWidth(0, 400)  # Strategy
        self.strategy_pnl_table.setColumnWidth(1, 200)  # PnL

        strategies = [
            "Strat 1: 1min 8-21-50 EMA Trend Rider",
            "Strat 2: 5min 50 EMA Cross with ATR Sell",
            "Strat 3: 2min Candle Break",
            "Strat 4: 2min 8/21 EMA Cross with ATR Sell"
        ]

        pnl_font = QFont("Arial", 14, QFont.Bold)  # Larger bold font for PnL values

        for i, strategy in enumerate(strategies):
            self.strategy_pnl_table.setItem(i, 0, QTableWidgetItem(strategy))
            pnl_item = QTableWidgetItem("0.00")
            pnl_item.setForeground(self.positive_color)
            self.strategy_pnl_table.setItem(i, 1, pnl_item)

        header = self.strategy_pnl_table.horizontalHeader()
        header.setFont(self.header_font)
        header.setDefaultAlignment(Qt.AlignLeft)

        layout.addWidget(self.strategy_pnl_table)
        group.setLayout(layout)
        self.main_layout.addWidget(group)

    def create_total_pnl_section(self):
        group = QGroupBox("Total Session P&L for the Day")
        group_font = QFont("Arial", 16, QFont.Bold)  # Larger font for group title
        group.setFont(group_font)
        layout = QHBoxLayout()

        self.total_pnl_label = QLabel("0.00")
        self.total_pnl_label.setAlignment(Qt.AlignCenter)
        # Much larger font for total PnL
        total_pnl_font = QFont("Arial", 24, QFont.Bold)  # Increased to 24pt
        self.total_pnl_label.setFont(total_pnl_font)
        self.total_pnl_label.setStyleSheet(f"color: {self.positive_color.name()}")

        # Set minimum height for better visibility
        self.total_pnl_label.setMinimumHeight(60)

        layout.addWidget(self.total_pnl_label)
        group.setLayout(layout)
        self.main_layout.addWidget(group)

    def create_system_log_section(self):
        group = QGroupBox("System / Error Logs")
        group.setFont(self.header_font)
        layout = QVBoxLayout()

        self.system_log = QTextEdit()
        self.system_log.setFont(self.default_font)
        self.system_log.setReadOnly(True)
        self.system_log.setMinimumHeight(150)

        layout.addWidget(self.system_log)
        group.setLayout(layout)
        self.main_layout.addWidget(group)

    def create_control_buttons(self):
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(20)
        button_layout.setContentsMargins(20, 10, 20, 10)

        # Updated button styles with more vibrant colors and better visibility
        base_style = """
            QPushButton {
                font-size: 16pt;
                font-weight: bold;
                padding: 15px 30px;
                border-radius: 8px;
                min-width: 300px;
                min-height: 60px;
                margin: 10px;
                border: none;
                color: white;
            }
            QPushButton:hover {
                border: 2px solid white;
                opacity: 0.9;
            }
        """

        # Start Trading Button (Green)
        start_style = base_style + """
            QPushButton {
                background-color: #2E8B57;  /* Sea Green */
            }
            QPushButton:hover {
                background-color: #3CB371;  /* Medium Sea Green */
            }
        """

        # Stop Trading Button (Orange)
        stop_style = base_style + """
            QPushButton {
                background-color: #FF8C00;  /* Dark Orange */
            }
            QPushButton:hover {
                background-color: #FFA500;  /* Orange */
            }
        """

        # Emergency Shutdown Button (Dark Red)
        emergency_style = base_style + """
            QPushButton {
                background-color: #8B0000;  /* Dark Red */
            }
            QPushButton:hover {
                background-color: #B22222;  /* Fire Brick */
            }
        """

        self.start_button = QPushButton("Start Trading")
        self.start_button.setFont(self.button_font)
        self.start_button.setStyleSheet(start_style)
        self.start_button.setFixedSize(300, 60)

        self.stop_button = QPushButton("Stop Trading")
        self.stop_button.setFont(self.button_font)
        self.stop_button.setStyleSheet(stop_style)
        self.stop_button.setFixedSize(300, 60)

        self.emergency_button = QPushButton("Emergency Shutdown")
        self.emergency_button.setFont(self.button_font)
        self.emergency_button.setStyleSheet(emergency_style)
        self.emergency_button.setFixedSize(300, 60)

        # Add spacers for centering
        button_layout.addStretch(1)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.emergency_button)
        button_layout.addStretch(1)

        self.main_layout.addWidget(button_container)

    def setup_timer(self):
        """Setup timer for updating time display"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second

    def update_time(self):
        """Update the time display"""
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        self.time_label.setText(f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {current_time}")

    def update_pnl_color(self, widget, value):
        """Helper function to set PnL colors"""
        try:
            pnl_value = float(value)
            color = self.positive_color if pnl_value >= 0 else self.negative_color
            if isinstance(widget, QLabel):
                widget.setStyleSheet(f"color: {color.name()}")
            elif isinstance(widget, QTableWidgetItem):
                widget.setForeground(color)
        except ValueError:
            pass