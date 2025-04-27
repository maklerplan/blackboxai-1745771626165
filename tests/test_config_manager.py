import pytest
import yaml
import tempfile
from pathlib import Path
from src.config_manager import (
    ConfigManager, 
    MonitoringConfig,
    ProcessingConfig,
    NotificationConfig,
    UIConfig,
    DatabaseConfig,
    LoggingConfig
)

@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    config = {
        'monitoring': {
            'enabled': True,
            'check_interval': 5,
            'folders': {
                'offers': '/test/offers',
                'invoices': '/test/invoices'
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
                'webhook_url': 'https://hooks.slack.com/test',
                'channel': '#test-channel',
                'notify_on': {
                    'price_discrepancies': True,
                    'quantity_mismatches': True,
                    'missing_items': True,
                    'successful_comparisons': False
                },
                'thresholds': {
                    'price_difference': 1.0,
                    'quantity_difference': 5
                }
            }
        },
        'ui': {
            'theme': 'dark',
            'window': {
                'width': 1200,
                'height': 800
            },
            'auto_refresh': True,
            'refresh_interval': 30
        },
        'database': {
            'path': 'test/db.sqlite',
            'retention_days': 60
        },
        'logging': {
            'level': 'DEBUG',
            'file': 'test/app.log',
            'max_size': 5242880,
            'backup_count': 3
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        yaml.dump(config, tmp)
        return tmp.name

@pytest.fixture
def config_manager(temp_config_file):
    """Create ConfigManager instance with temporary config file"""
    return ConfigManager(temp_config_file)

def test_load_config(config_manager):
    """Test loading configuration from file"""
    assert config_manager.load_config()
    assert config_manager.config is not None
    assert 'monitoring' in config_manager.config
    assert 'processing' in config_manager.config
    assert 'notifications' in config_manager.config

def test_get_monitoring_config(config_manager):
    """Test retrieving monitoring configuration"""
    config = config_manager.get_monitoring_config()
    
    assert isinstance(config, MonitoringConfig)
    assert config.enabled is True
    assert config.check_interval == 5
    assert config.offers_folder == '/test/offers'
    assert config.invoices_folder == '/test/invoices'

def test_get_processing_config(config_manager):
    """Test retrieving processing configuration"""
    config = config_manager.get_processing_config()
    
    assert isinstance(config, ProcessingConfig)
    assert config.price_tolerance == 0.02
    assert config.extraction_method == 'intelligent'
    assert config.track_partial_deliveries is True

def test_get_notification_config(config_manager):
    """Test retrieving notification configuration"""
    config = config_manager.get_notification_config()
    
    assert isinstance(config, NotificationConfig)
    assert config.enabled is True
    assert config.webhook_url == 'https://hooks.slack.com/test'
    assert config.channel == '#test-channel'
    assert config.notify_price_discrepancies is True
    assert config.notify_quantity_mismatches is True
    assert config.price_threshold == 1.0
    assert config.quantity_threshold == 5

def test_get_ui_config(config_manager):
    """Test retrieving UI configuration"""
    config = config_manager.get_ui_config()
    
    assert isinstance(config, UIConfig)
    assert config.theme == 'dark'
    assert config.window_width == 1200
    assert config.window_height == 800
    assert config.auto_refresh is True
    assert config.refresh_interval == 30

def test_get_database_config(config_manager):
    """Test retrieving database configuration"""
    config = config_manager.get_database_config()
    
    assert isinstance(config, DatabaseConfig)
    assert config.path == 'test/db.sqlite'
    assert config.retention_days == 60

def test_get_logging_config(config_manager):
    """Test retrieving logging configuration"""
    config = config_manager.get_logging_config()
    
    assert isinstance(config, LoggingConfig)
    assert config.level == 'DEBUG'
    assert config.file == 'test/app.log'
    assert config.max_size == 5242880
    assert config.backup_count == 3

def test_update_monitoring_config(config_manager):
    """Test updating monitoring configuration"""
    assert config_manager.update_monitoring_config(
        enabled=False,
        check_interval=10,
        offers_folder='/new/offers',
        invoices_folder='/new/invoices'
    )
    
    config = config_manager.get_monitoring_config()
    assert config.enabled is False
    assert config.check_interval == 10
    assert config.offers_folder == '/new/offers'
    assert config.invoices_folder == '/new/invoices'

def test_update_notification_config(config_manager):
    """Test updating notification configuration"""
    assert config_manager.update_notification_config(
        enabled=False,
        webhook_url='https://hooks.slack.com/new',
        channel='#new-channel',
        notify_price_discrepancies=False
    )
    
    config = config_manager.get_notification_config()
    assert config.enabled is False
    assert config.webhook_url == 'https://hooks.slack.com/new'
    assert config.channel == '#new-channel'
    assert config.notify_price_discrepancies is False

def test_update_processing_config(config_manager):
    """Test updating processing configuration"""
    assert config_manager.update_processing_config(
        price_tolerance=0.05,
        extraction_method='text_only',
        track_partial_deliveries=False
    )
    
    config = config_manager.get_processing_config()
    assert config.price_tolerance == 0.05
    assert config.extraction_method == 'text_only'
    assert config.track_partial_deliveries is False

def test_reset_to_defaults(config_manager):
    """Test resetting configuration to defaults"""
    # First modify some settings
    config_manager.update_monitoring_config(enabled=False)
    config_manager.update_processing_config(price_tolerance=0.05)
    
    # Then reset to defaults
    assert config_manager.reset_to_defaults()
    
    # Verify defaults are restored
    monitoring_config = config_manager.get_monitoring_config()
    assert monitoring_config.enabled is True
    assert monitoring_config.check_interval == 5
    
    processing_config = config_manager.get_processing_config()
    assert processing_config.price_tolerance == 0.02
    assert processing_config.extraction_method == 'intelligent'

def test_save_and_load_config(temp_config_file):
    """Test saving and loading configuration"""
    # Create a new config manager
    config_manager = ConfigManager(temp_config_file)
    
    # Modify some settings
    config_manager.update_monitoring_config(enabled=False)
    config_manager.update_processing_config(price_tolerance=0.05)
    
    # Create a new config manager instance to load the saved config
    new_config_manager = ConfigManager(temp_config_file)
    
    # Verify settings were saved and loaded correctly
    monitoring_config = new_config_manager.get_monitoring_config()
    assert monitoring_config.enabled is False
    
    processing_config = new_config_manager.get_processing_config()
    assert processing_config.price_tolerance == 0.05

def test_invalid_config_file():
    """Test handling of invalid configuration file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        tmp.write("invalid: yaml: content:")
        
    config_manager = ConfigManager(tmp.name)
    assert not config_manager.load_config()
    
    # Clean up
    Path(tmp.name).unlink()

if __name__ == '__main__':
    pytest.main([__file__])
