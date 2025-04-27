#!/usr/bin/env python3
"""
Setup verification script for PDF Comparison Tool.
This script tests all major components and dependencies.
"""

import sys
import os
import tempfile
from pathlib import Path
import logging
from datetime import datetime
import yaml
import requests
import fpdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check Python version"""
    logger.info("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version {sys.version} OK")
    return True

def check_dependencies():
    """Check required Python packages"""
    logger.info("Checking dependencies...")
    required_packages = [
        'PyQt6',
        'pdfplumber',
        'PyPDF2',
        'watchdog',
        'requests',
        'SQLAlchemy',
        'PyYAML',
        'pytest'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package}")
        except ImportError:
            logger.error(f"✗ {package} not found")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def create_test_pdf():
    """Create a test PDF file"""
    logger.info("Creating test PDF...")
    try:
        pdf = fpdf.FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Test PDF Document", ln=1, align='C')
        pdf.cell(200, 10, txt="Item Code: TEST123", ln=1, align='L')
        pdf.cell(200, 10, txt="Quantity: 10", ln=1, align='L')
        pdf.cell(200, 10, txt="Price: €25.00", ln=1, align='L')
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf.output(tmp.name)
            logger.info(f"Test PDF created at {tmp.name}")
            return tmp.name
    except Exception as e:
        logger.error(f"Error creating test PDF: {str(e)}")
        return None

def test_pdf_processing():
    """Test PDF processing capabilities"""
    logger.info("Testing PDF processing...")
    try:
        import pdfplumber
        
        pdf_path = create_test_pdf()
        if not pdf_path:
            return False
        
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text()
            if "TEST123" in text and "10" in text and "25.00" in text:
                logger.info("PDF processing test successful")
                return True
            else:
                logger.error("PDF processing test failed - content not found")
                return False
    except Exception as e:
        logger.error(f"PDF processing test failed: {str(e)}")
        return False
    finally:
        if pdf_path:
            try:
                os.unlink(pdf_path)
            except:
                pass

def test_file_monitoring():
    """Test file monitoring capabilities"""
    logger.info("Testing file monitoring...")
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        observer = Observer()
        observer.start()
        observer.stop()
        observer.join()
        
        logger.info("File monitoring test successful")
        return True
    except Exception as e:
        logger.error(f"File monitoring test failed: {str(e)}")
        return False

def test_database():
    """Test database operations"""
    logger.info("Testing database operations...")
    try:
        from sqlalchemy import create_engine, Column, Integer, String
        from sqlalchemy.ext.declarative import declarative_base
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
            engine = create_engine(f'sqlite:///{tmp.name}')
            Base = declarative_base()
            
            class TestModel(Base):
                __tablename__ = 'test'
                id = Column(Integer, primary_key=True)
                name = Column(String)
            
            Base.metadata.create_all(engine)
            logger.info("Database test successful")
            return True
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return False

def test_slack_connectivity(webhook_url=None):
    """Test Slack connectivity"""
    logger.info("Testing Slack connectivity...")
    
    if not webhook_url:
        logger.warning("No Slack webhook URL provided - skipping test")
        return None
    
    try:
        response = requests.post(
            webhook_url,
            json={
                "text": "PDF Comparison Tool - Setup Test",
                "blocks": [{
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🔧 Setup verification test successful!"
                    }
                }]
            }
        )
        
        if response.status_code == 200:
            logger.info("Slack connectivity test successful")
            return True
        else:
            logger.error(f"Slack test failed: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Slack test failed: {str(e)}")
        return False

def test_gui():
    """Test GUI capabilities"""
    logger.info("Testing GUI capabilities...")
    try:
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication([])
        logger.info("GUI test successful")
        return True
    except Exception as e:
        logger.error(f"GUI test failed: {str(e)}")
        return False

def check_folders():
    """Check required folders exist"""
    logger.info("Checking required folders...")
    required_folders = ['src', 'tests', 'config']
    
    missing_folders = []
    for folder in required_folders:
        if not Path(folder).exists():
            logger.error(f"✗ {folder}/ not found")
            missing_folders.append(folder)
        else:
            logger.info(f"✓ {folder}/")
    
    return len(missing_folders) == 0

def check_config():
    """Check configuration file"""
    logger.info("Checking configuration...")
    config_path = Path('config/settings.yaml')
    
    if not config_path.exists():
        logger.error("Configuration file not found")
        return False
    
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            
        required_sections = ['monitoring', 'processing', 'notifications', 'ui', 'database', 'logging']
        missing_sections = []
        
        for section in required_sections:
            if section not in config:
                missing_sections.append(section)
        
        if missing_sections:
            logger.error(f"Missing configuration sections: {', '.join(missing_sections)}")
            return False
        
        logger.info("Configuration check successful")
        return True
    except Exception as e:
        logger.error(f"Error checking configuration: {str(e)}")
        return False

def main():
    """Run all setup verification tests"""
    logger.info("Starting setup verification...")
    logger.info("=" * 50)
    
    results = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Required Folders": check_folders(),
        "Configuration": check_config(),
        "PDF Processing": test_pdf_processing(),
        "File Monitoring": test_file_monitoring(),
        "Database": test_database(),
        "GUI": test_gui()
    }
    
    # Get Slack webhook URL from config if available
    try:
        with open('config/settings.yaml') as f:
            config = yaml.safe_load(f)
            webhook_url = config.get('notifications', {}).get('slack', {}).get('webhook_url')
            if webhook_url:
                results["Slack Connectivity"] = test_slack_connectivity(webhook_url)
    except:
        pass
    
    logger.info("\nTest Results:")
    logger.info("=" * 50)
    
    all_passed = True
    for test, passed in results.items():
        if passed is None:
            status = "SKIPPED"
        else:
            status = "PASSED" if passed else "FAILED"
            if not passed and passed is not None:
                all_passed = False
        logger.info(f"{test}: {status}")
    
    logger.info("=" * 50)
    if all_passed:
        logger.info("All tests passed! The system is ready to use.")
        return 0
    else:
        logger.error("Some tests failed. Please check the logs and fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
