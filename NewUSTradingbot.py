from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QFormLayout, QGroupBox, QLabel,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
                             QLineEdit, QComboBox, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QSettings, QDateTime
from PyQt5.QtGui import QFont, QPalette, QColor
import sys
import json
from datetime import datetime
from trading_dashboard import TradingDashboard

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        self.setWindowTitle(f"Trading Bot Configuration")
        self.setMinimumSize(1000, 1600)  # Increased window size

        # Set default font for the entire application
        self.default_font = QFont("Arial", 12)  # Increased base font size
        self.setFont(self.default_font)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)

        # Add user information
        self.add_user_info()

        # Initialize UI components
        self.create_global_settings()
        self.create_position_settings()
        self.create_strategy_settings()
        self.create_control_buttons()
        self.add_position_size_example()

        # Load any saved settings
        self.load_settings()

    def add_user_info(self):
        info_group = QGroupBox("Session Information")
        layout = QFormLayout()

        # Set larger font for group box title
        title_font = QFont("Arial", 14, QFont.Bold)
        info_group.setFont(title_font)

        # Add current date/time and user info with specified format
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        time_label = QLabel(f"{current_time} UTC")
        user_label = QLabel("Kish19691969")

        # Make labels larger
        info_font = QFont("Arial", 12)
        time_label.setFont(info_font)
        user_label.setFont(info_font)

        # Add to layout with larger font for labels
        datetime_label = QLabel("Current Date/Time (UTC):")
        user_title_label = QLabel("Current User:")
        datetime_label.setFont(info_font)
        user_title_label.setFont(info_font)

        layout.addRow(datetime_label, time_label)
        layout.addRow(user_title_label, user_label)

        info_group.setLayout(layout)
        self.main_layout.addWidget(info_group)

    def create_global_settings(self):
        global_group = QGroupBox("Global Settings")
        title_font = QFont("Arial", 14, QFont.Bold)
        global_group.setFont(title_font)

        layout = QFormLayout()

        # Account Settings
        self.account_id = QLineEdit()
        self.account_id.setFont(self.default_font)
        self.account_id.setMinimumHeight(30)  # Make input field taller

        # Trading Hours
        self.trading_start = QComboBox()
        self.trading_end = QComboBox()
        self.trading_start.setFont(self.default_font)
        self.trading_end.setFont(self.default_font)
        self.trading_start.setMinimumHeight(30)  # Make comboboxes taller
        self.trading_end.setMinimumHeight(30)

        # Add times in 30-minute intervals
        for hour in range(24):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                self.trading_start.addItem(time_str)
                self.trading_end.addItem(time_str)

        # Set default trading hours
        self.trading_start.setCurrentText("09:30")
        self.trading_end.setCurrentText("16:00")

        # Add items to layout with larger font for labels
        label_font = QFont("Arial", 12)
        for text, widget in [
            ("Account ID:", self.account_id),
            ("Trading Start (UTC):", self.trading_start),
            ("Trading End (UTC):", self.trading_end)
        ]:
            label = QLabel(text)
            label.setFont(label_font)
            layout.addRow(label, widget)

        global_group.setLayout(layout)
        self.main_layout.addWidget(global_group)

    def style_spinbox(self, spinbox):
        spinbox.setFont(self.default_font)
        spinbox.setMinimumHeight(30)  # Make spinboxes taller

    def create_position_settings(self):
        position_group = QGroupBox("Position Management")
        title_font = QFont("Arial", 14, QFont.Bold)
        position_group.setFont(title_font)

        layout = QFormLayout()

        # Max Concurrent Positions
        self.max_positions = QSpinBox()
        self.style_spinbox(self.max_positions)
        self.max_positions.setRange(1, 10)
        self.max_positions.setValue(5)

        # Max Dollar Amount per Position
        self.max_position_dollars = QDoubleSpinBox()
        self.style_spinbox(self.max_position_dollars)
        self.max_position_dollars.setRange(1000, 50000)
        self.max_position_dollars.setValue(5000)
        self.max_position_dollars.setPrefix("$")
        self.max_position_dollars.setDecimals(2)
        self.max_position_dollars.setSingleStep(100)

        # Minimum Stock Price
        self.min_stock_price = QDoubleSpinBox()
        self.style_spinbox(self.min_stock_price)
        self.min_stock_price.setRange(1, 1000)
        self.min_stock_price.setValue(5)
        self.min_stock_price.setPrefix("$")
        self.min_stock_price.setDecimals(2)

        # Maximum Stock Price
        self.max_stock_price = QDoubleSpinBox()
        self.style_spinbox(self.max_stock_price)
        self.max_stock_price.setRange(1, 1000)
        self.max_stock_price.setValue(200)
        self.max_stock_price.setPrefix("$")
        self.max_stock_price.setDecimals(2)

        # Add items to layout with larger font for labels
        label_font = QFont("Arial", 12)
        for text, widget in [
            ("Max Concurrent Positions:", self.max_positions),
            ("Max $ per Position:", self.max_position_dollars),
            ("Min Stock Price:", self.min_stock_price),
            ("Max Stock Price:", self.max_stock_price)
        ]:
            label = QLabel(text)
            label.setFont(label_font)
            layout.addRow(label, widget)

        position_group.setLayout(layout)
        self.main_layout.addWidget(position_group)

    def add_position_size_example(self):
        example_group = QGroupBox("Position Size Calculator Example")
        title_font = QFont("Arial", 14, QFont.Bold)
        example_group.setFont(title_font)

        layout = QVBoxLayout()

        # Add explanation with larger font
        explanation = QLabel(
            "Position size will be calculated as:\n"
            "Number of Shares = Floor(Max $ per Position / Stock Price)\n"
            "Example calculations based on current Max $ per Position setting:"
        )
        explanation.setFont(self.default_font)
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        # Create example table
        example_frame = QFrame()
        example_layout = QFormLayout()

        examples = [
            ("$25 stock", "200 shares ($5,000 total)"),
            ("$50 stock", "100 shares ($5,000 total)"),
            ("$100 stock", "50 shares ($5,000 total)"),
            ("$180 stock", "27 shares ($4,860 total)")
        ]

        # Add examples with larger font
        label_font = QFont("Arial", 12)
        for price, shares in examples:
            label = QLabel(price)
            value = QLabel(shares)
            label.setFont(label_font)
            value.setFont(label_font)
            example_layout.addRow(label, value)

        example_frame.setLayout(example_layout)
        layout.addWidget(example_frame)

        example_group.setLayout(layout)
        self.main_layout.addWidget(example_group)

    def update_session_info(self):
        current_time = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        self.time_label.setText(f"{current_time} UTC")

    def create_strategy_settings(self):
        strategy_group = QGroupBox("Strategy Selection")
        title_font = QFont("Arial", 14, QFont.Bold)
        strategy_group.setFont(title_font)

        layout = QVBoxLayout()

        # Strategy configurations
        self.strategies = {
            "Strategy 1 : 2 Min 8-21-50 EMA Trend Rider ": {
                "enabled": False,
                "profit_target_percent": 3.0,
                "stop_loss_percent": 2.0,
                "max_trades_per_day": 5
            },
            "Strategy 2 : 5 Min EMA Cross with ATR Sell": {
                "enabled": False,
                "profit_target_percent": 3.0,
                "stop_loss_percent": 2.0,
                "max_trades_per_day": 5
            },
            "Strategy 3 : 2 Min Candle High Break": {
                "enabled": False,
                "profit_target_percent": 3.0,
                "stop_loss_percent": 2.0,
                "max_trades_per_day": 5
            },
            "Strategy 4 : 5 Min 8/21 EMA Cross": {
                "enabled": False,
                "profit_target_percent": 3.0,
                "stop_loss_percent": 2.0,
                "max_trades_per_day": 5
            }
        }

        self.strategy_widgets = {}

        for strategy_name, settings in self.strategies.items():
            strategy_box = QGroupBox(strategy_name)
            strategy_box.setFont(QFont("Arial", 12, QFont.Bold))
            strategy_layout = QFormLayout()

            # Enable/Disable checkbox with larger font
            enable_checkbox = QCheckBox("Enable")
            enable_checkbox.setFont(self.default_font)
            strategy_layout.addRow(enable_checkbox)

            # Create and style spinboxes
            profit_target = QDoubleSpinBox()
            stop_loss = QDoubleSpinBox()
            max_trades = QSpinBox()

            for spinbox in [profit_target, stop_loss, max_trades]:
                self.style_spinbox(spinbox)

            # Configure spinboxes
            profit_target.setRange(0.1, 20.0)
            profit_target.setSingleStep(0.1)
            profit_target.setValue(settings["profit_target_percent"])
            profit_target.setSuffix("%")

            stop_loss.setRange(0.1, 10.0)
            stop_loss.setSingleStep(0.1)
            stop_loss.setValue(settings["stop_loss_percent"])
            stop_loss.setSuffix("%")

            max_trades.setRange(1, 50)
            max_trades.setValue(settings["max_trades_per_day"])

            # Add items to layout with larger font for labels
            label_font = QFont("Arial", 12)
            for text, widget in [
                ("Profit Target %:", profit_target),
                ("Stop Loss %:", stop_loss),
                ("Max Trades/Day:", max_trades)
            ]:
                label = QLabel(text)
                label.setFont(label_font)
                strategy_layout.addRow(label, widget)

            strategy_box.setLayout(strategy_layout)
            layout.addWidget(strategy_box)

            # Store widgets for later access
            self.strategy_widgets[strategy_name] = {
                "enable": enable_checkbox,
                "profit_target": profit_target,
                "stop_loss": stop_loss,
                "max_trades": max_trades
            }

        strategy_group.setLayout(layout)
        self.main_layout.addWidget(strategy_group)

    def create_control_buttons(self):
        button_layout = QHBoxLayout()

        # Create buttons with larger font and colors
        button_font = QFont("Arial", 14, QFont.Bold)

        # Save Button (Blue)
        self.save_button = QPushButton("Save Settings")
        self.save_button.setFont(button_font)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        # Load Button (Orange)
        self.load_button = QPushButton("Load Settings")
        self.load_button.setFont(button_font)
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)

        # Cancel Button (Red)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(button_font)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        # Start Trading Button (Green)
        self.start_button = QPushButton("Start Trading")
        self.start_button.setFont(button_font)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                min-width: 150px;
                min-height: 40px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)

        # Connect signals
        self.save_button.clicked.connect(self.save_settings)
        self.load_button.clicked.connect(self.load_settings)
        self.cancel_button.clicked.connect(self.cancel_trading)
        self.start_button.clicked.connect(self.start_trading)

        # Add buttons to layout with spacing
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.start_button)

        # Add some spacing between buttons
        button_layout.setSpacing(20)

        self.main_layout.addLayout(button_layout)

    def save_settings(self):
        settings = {
            "global": {
                "account_id": self.account_id.text(),
                "trading_start": self.trading_start.currentText(),
                "trading_end": self.trading_end.currentText()
            },
            "position": {
                "max_positions": self.max_positions.value(),
                "max_position_dollars": self.max_position_dollars.value(),
                "min_stock_price": self.min_stock_price.value(),
                "max_stock_price": self.max_stock_price.value()
            },
            "strategies": {}
        }

        # Save strategy settings
        for strategy_name, widgets in self.strategy_widgets.items():
            settings["strategies"][strategy_name] = {
                "enabled": widgets["enable"].isChecked(),
                "profit_target_percent": widgets["profit_target"].value(),
                "stop_loss_percent": widgets["stop_loss"].value(),
                "max_trades_per_day": widgets["max_trades"].value()
            }

        try:
            # Save to file with timestamp
            timestamp = QDateTime.currentDateTime().toString('yyyy-MM-dd_HH-mm-ss')
            filename = f'trading_config_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump(settings, f, indent=4)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setFont(self.default_font)
            msg.setText("Settings saved successfully!")
            msg.setWindowTitle("Success")
            msg.exec_()

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setFont(self.default_font)
            msg.setText(f"Failed to save settings: {str(e)}")
            msg.setWindowTitle("Error")
            msg.exec_()

    def load_settings(self):
        try:
            # Show file dialog with larger font
            from PyQt5.QtWidgets import QFileDialog
            options = QFileDialog.Options()
            fileName, _ = QFileDialog.getOpenFileName(
                self,
                "Load Trading Configuration",
                "",
                "JSON Files (*.json)",
                options=options
            )

            if fileName:
                with open(fileName, 'r') as f:
                    settings = json.load(f)

                # Load global settings
                global_settings = settings.get("global", {})
                self.account_id.setText(global_settings.get("account_id", ""))
                self.trading_start.setCurrentText(global_settings.get("trading_start", "09:30"))
                self.trading_end.setCurrentText(global_settings.get("trading_end", "16:00"))

                # Load position settings
                position_settings = settings.get("position", {})
                self.max_positions.setValue(position_settings.get("max_positions", 5))
                self.max_position_dollars.setValue(position_settings.get("max_position_dollars", 5000))
                self.min_stock_price.setValue(position_settings.get("min_stock_price", 5))
                self.max_stock_price.setValue(position_settings.get("max_stock_price", 200))

                # Load strategy settings
                strategy_settings = settings.get("strategies", {})
                for strategy_name, strategy_data in strategy_settings.items():
                    if strategy_name in self.strategy_widgets:
                        widgets = self.strategy_widgets[strategy_name]
                        widgets["enable"].setChecked(strategy_data.get("enabled", False))
                        widgets["profit_target"].setValue(strategy_data.get("profit_target_percent", 3.0))
                        widgets["stop_loss"].setValue(strategy_data.get("stop_loss_percent", 2.0))
                        widgets["max_trades"].setValue(strategy_data.get("max_trades_per_day", 5))

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setFont(self.default_font)
                msg.setText("Settings loaded successfully!")
                msg.setWindowTitle("Success")
                msg.exec_()

        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setFont(self.default_font)
            msg.setText(f"Failed to load settings: {str(e)}")
            msg.setWindowTitle("Warning")
            msg.exec_()

    def validate_settings(self):
        if not self.account_id.text().strip():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setFont(self.default_font)
            msg.setText("Please enter an Account ID!")
            msg.setWindowTitle("Validation Error")
            msg.exec_()
            return False

        if self.min_stock_price.value() >= self.max_stock_price.value():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setFont(self.default_font)
            msg.setText("Maximum stock price must be greater than minimum stock price!")
            msg.setWindowTitle("Validation Error")
            msg.exec_()
            return False

        start_time = self.trading_start.currentText()
        end_time = self.trading_end.currentText()
        if start_time >= end_time:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setFont(self.default_font)
            msg.setText("Trading end time must be after start time!")
            msg.setWindowTitle("Validation Error")
            msg.exec_()
            return False

        return True

    def cancel_trading(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setFont(self.default_font)
        msg.setText("Are you sure you want to exit?")
        msg.setWindowTitle("Confirm Exit")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            QApplication.quit()

    def start_trading(self):
        # Validate settings before starting
        if not self.validate_settings():
            return

        # Check if any strategy is enabled
        enabled_strategies = [name for name, widgets in self.strategy_widgets.items()
                              if widgets["enable"].isChecked()]

        if not enabled_strategies:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setFont(self.default_font)
            msg.setText("Please enable at least one strategy!")
            msg.setWindowTitle("Warning")
            msg.exec_()
            return

        # Prepare confirmation message
        confirmation = (
            f"Current Date/Time (UTC): {QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')}\n\n"
            f"Trading Configuration Summary:\n"
            f"Account ID: {self.account_id.text()}\n"
            f"Max Positions: {self.max_positions.value()}\n"
            f"Max $ per Position: ${self.max_position_dollars.value():.2f}\n"
            f"Stock Price Range: ${self.min_stock_price.value():.2f} - ${self.max_stock_price.value():.2f}\n"
            f"Trading Hours (UTC): {self.trading_start.currentText()} - {self.trading_end.currentText()}\n\n"
            f"Enabled Strategies:\n"
        )

        for strategy in enabled_strategies:
            widgets = self.strategy_widgets[strategy]
            confirmation += (
                f"\n{strategy}:\n"
                f"- Profit Target: {widgets['profit_target'].value()}%\n"
                f"- Stop Loss: {widgets['stop_loss'].value()}%\n"
                f"- Max Trades/Day: {widgets['max_trades'].value()}\n"
            )

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setFont(self.default_font)
        msg.setText(confirmation + "\n\nDo you want to proceed?")
        msg.setWindowTitle("Confirm Trading Start")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            try:
                # Get enabled strategy settings
                strategy_settings = {
                    name: {
                        "profit_target": self.strategy_widgets[name]["profit_target"].value(),
                        "stop_loss": self.strategy_widgets[name]["stop_loss"].value(),
                        "max_trades": self.strategy_widgets[name]["max_trades"].value()
                    }
                    for name in enabled_strategies
                }

                # Create and show the trading dashboard
                self.trading_dashboard = TradingDashboard(
                    account_id=self.account_id.text(),
                    trading_start=self.trading_start.currentText(),
                    trading_end=self.trading_end.currentText(),
                    max_positions=self.max_positions.value(),
                    max_position_dollars=self.max_position_dollars.value(),
                    min_stock_price=self.min_stock_price.value(),
                    max_stock_price=self.max_stock_price.value(),
                    strategy_settings=strategy_settings
                )
                self.trading_dashboard.show()
                self.close()
            except Exception as e:
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setFont(self.default_font)
                error_msg.setText(f"Error starting trading dashboard: {str(e)}")
                error_msg.setWindowTitle("Error")
                error_msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show the window
    window = SettingsWindow()
    window.show()

    sys.exit(app.exec_())