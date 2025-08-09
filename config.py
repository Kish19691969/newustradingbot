from datetime import datetime
import json
import os

class TradingConfig:
    def __init__(self):
        self.config_file = 'trading_config.json'
        self.user_login = "Kish19691969"
        self.last_updated = "2025-08-09 16:25:09"  # Your exact current timestamp
        self.load_config()

    def load_config(self):
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.user_login = config.get('user_login', self.user_login)
                    self.last_updated = config.get('last_updated', self.last_updated)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        """Save current configuration to file"""
        config = {
            'user_login': self.user_login,
            'last_updated': self.last_updated
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def update_timestamp(self):
        """Update timestamp in exact required format"""
        self.last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.save_config()

    def get_formatted_timestamp(self):
        """Get timestamp in exactly specified format"""
        return f"Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {self.last_updated}"

    def get_formatted_user(self):
        """Get user login in exactly specified format"""
        return f"Current User's Login: {self.user_login}"