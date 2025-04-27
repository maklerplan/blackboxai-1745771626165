import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MonitoringConfig:
    enabled: bool
    check_interval: int
    offers_folder: str
    invoices_folder: str

@dataclass
class ProcessingConfig:
    price_tolerance: float
    extraction_method: str
    track_partial_deliveries: bool

@dataclass
class NotificationConfig:
    enabled: bool
    webhook_url: str
    channel: str
    notify_price_discrepancies: bool
    notify_quantity_mismatches: bool
    notify_missing_items: bool
    notify_successful_comparisons: bool
    price_threshold: float
    quantity_threshold: int

@dataclass
class UIConfig:
    theme: str
    window_width: int
    window_height: int
    auto_refresh: bool
    refresh_interval: int

@dataclass
class DatabaseConfig:
    path: str
    retention_days: int

@dataclass
class LoggingConfig:
    level: str
    file: str
    max_size: int
    backup_count: int

class ConfigManager:
    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Load configuration
        self.load_config()

    def load_config(self) -> bool:
        """
        Load configuration from YAML file
        
        Returns:
            bool: True if configuration was loaded successfully
        """
        try:
            config_file = Path(self.config_path)
            
            if not config_file.exists():
                logging.error(f"Configuration file not found: {self.config_path}")
                return False
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            logging.info(f"Loaded configuration from {self.config_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading configuration: {str(e)}")
            return False

    def save_config(self) -> bool:
        """
        Save current configuration to YAML file
        
        Returns:
            bool: True if configuration was saved successfully
        """
        try:
            config_file = Path(self.config_path)
            
            # Ensure directory exists
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logging.info(f"Saved configuration to {self.config_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving configuration: {str(e)}")
            return False

    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration"""
        monitoring = self.config.get('monitoring', {})
        return MonitoringConfig(
            enabled=monitoring.get('enabled', True),
            check_interval=monitoring.get('check_interval', 5),
            offers_folder=monitoring.get('folders', {}).get('offers', ''),
            invoices_folder=monitoring.get('folders', {}).get('invoices', '')
        )

    def get_processing_config(self) -> ProcessingConfig:
        """Get PDF processing configuration"""
        processing = self.config.get('processing', {})
        return ProcessingConfig(
            price_tolerance=processing.get('price_tolerance', 0.02),
            extraction_method=processing.get('extraction_method', 'intelligent'),
            track_partial_deliveries=processing.get('track_partial_deliveries', True)
        )

    def get_notification_config(self) -> NotificationConfig:
        """Get notification configuration"""
        notifications = self.config.get('notifications', {}).get('slack', {})
        notify_on = notifications.get('notify_on', {})
        thresholds = notifications.get('thresholds', {})
        
        return NotificationConfig(
            enabled=notifications.get('enabled', True),
            webhook_url=notifications.get('webhook_url', ''),
            channel=notifications.get('channel', '#pdf-comparison-alerts'),
            notify_price_discrepancies=notify_on.get('price_discrepancies', True),
            notify_quantity_mismatches=notify_on.get('quantity_mismatches', True),
            notify_missing_items=notify_on.get('missing_items', True),
            notify_successful_comparisons=notify_on.get('successful_comparisons', False),
            price_threshold=float(thresholds.get('price_difference', 0.0)),
            quantity_threshold=int(thresholds.get('quantity_difference', 0))
        )

    def get_ui_config(self) -> UIConfig:
        """Get UI configuration"""
        ui = self.config.get('ui', {})
        window = ui.get('window', {})
        
        return UIConfig(
            theme=ui.get('theme', 'light'),
            window_width=window.get('width', 1024),
            window_height=window.get('height', 768),
            auto_refresh=ui.get('auto_refresh', True),
            refresh_interval=ui.get('refresh_interval', 60)
        )

    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration"""
        database = self.config.get('database', {})
        return DatabaseConfig(
            path=database.get('path', 'data/comparison_history.db'),
            retention_days=database.get('retention_days', 90)
        )

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        logging_config = self.config.get('logging', {})
        return LoggingConfig(
            level=logging_config.get('level', 'INFO'),
            file=logging_config.get('file', 'logs/comparison_tool.log'),
            max_size=logging_config.get('max_size', 10485760),
            backup_count=logging_config.get('backup_count', 5)
        )

    def update_monitoring_config(self, 
                               enabled: Optional[bool] = None,
                               check_interval: Optional[int] = None,
                               offers_folder: Optional[str] = None,
                               invoices_folder: Optional[str] = None) -> bool:
        """
        Update monitoring configuration
        
        Returns:
            bool: True if configuration was updated and saved successfully
        """
        try:
            if 'monitoring' not in self.config:
                self.config['monitoring'] = {}
            
            if enabled is not None:
                self.config['monitoring']['enabled'] = enabled
            
            if check_interval is not None:
                self.config['monitoring']['check_interval'] = check_interval
            
            if offers_folder is not None or invoices_folder is not None:
                if 'folders' not in self.config['monitoring']:
                    self.config['monitoring']['folders'] = {}
                
                if offers_folder is not None:
                    self.config['monitoring']['folders']['offers'] = offers_folder
                
                if invoices_folder is not None:
                    self.config['monitoring']['folders']['invoices'] = invoices_folder
            
            return self.save_config()
            
        except Exception as e:
            logging.error(f"Error updating monitoring configuration: {str(e)}")
            return False

    def update_notification_config(self,
                                 enabled: Optional[bool] = None,
                                 webhook_url: Optional[str] = None,
                                 channel: Optional[str] = None,
                                 **notify_settings) -> bool:
        """
        Update notification configuration
        
        Returns:
            bool: True if configuration was updated and saved successfully
        """
        try:
            if 'notifications' not in self.config:
                self.config['notifications'] = {'slack': {}}
            
            slack_config = self.config['notifications']['slack']
            
            if enabled is not None:
                slack_config['enabled'] = enabled
            
            if webhook_url is not None:
                slack_config['webhook_url'] = webhook_url
            
            if channel is not None:
                slack_config['channel'] = channel
            
            # Update notification triggers
            if 'notify_on' not in slack_config:
                slack_config['notify_on'] = {}
            
            for key, value in notify_settings.items():
                if key.startswith('notify_'):
                    setting = key.replace('notify_', '')
                    slack_config['notify_on'][setting] = value
            
            return self.save_config()
            
        except Exception as e:
            logging.error(f"Error updating notification configuration: {str(e)}")
            return False

    def update_processing_config(self,
                               price_tolerance: Optional[float] = None,
                               extraction_method: Optional[str] = None,
                               track_partial_deliveries: Optional[bool] = None) -> bool:
        """
        Update processing configuration
        
        Returns:
            bool: True if configuration was updated and saved successfully
        """
        try:
            if 'processing' not in self.config:
                self.config['processing'] = {}
            
            if price_tolerance is not None:
                self.config['processing']['price_tolerance'] = price_tolerance
            
            if extraction_method is not None:
                self.config['processing']['extraction_method'] = extraction_method
            
            if track_partial_deliveries is not None:
                self.config['processing']['track_partial_deliveries'] = track_partial_deliveries
            
            return self.save_config()
            
        except Exception as e:
            logging.error(f"Error updating processing configuration: {str(e)}")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values
        
        Returns:
            bool: True if configuration was reset and saved successfully
        """
        try:
            self.config = {
                'monitoring': {
                    'enabled': True,
                    'check_interval': 5,
                    'folders': {
                        'offers': '',
                        'invoices': ''
                    }
                },
                'processing': {
                    'price_tolerance': 0.02,
                    'extraction_method': 'intelligent',
                    'track_partial_deliveries': True
                },
                'notifications': {
                    'slack': {
                        'enabled': True,
                        'webhook_url': '',
                        'channel': '#pdf-comparison-alerts',
                        'notify_on': {
                            'price_discrepancies': True,
                            'quantity_mismatches': True,
                            'missing_items': True,
                            'successful_comparisons': False
                        },
                        'thresholds': {
                            'price_difference': 0.0,
                            'quantity_difference': 0
                        }
                    }
                },
                'ui': {
                    'theme': 'light',
                    'window': {
                        'width': 1024,
                        'height': 768
                    },
                    'auto_refresh': True,
                    'refresh_interval': 60
                },
                'database': {
                    'path': 'data/comparison_history.db',
                    'retention_days': 90
                },
                'logging': {
                    'level': 'INFO',
                    'file': 'logs/comparison_tool.log',
                    'max_size': 10485760,
                    'backup_count': 5
                }
            }
            
            return self.save_config()
            
        except Exception as e:
            logging.error(f"Error resetting configuration: {str(e)}")
            return False
