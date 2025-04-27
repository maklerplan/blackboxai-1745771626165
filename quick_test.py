#!/usr/bin/env python3
"""
Quick test script for PDF Comparison Tool.
Generates test PDFs and runs comparisons to demonstrate functionality.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
import shutil
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(cmd, cwd=None):
    """Run a command and return its output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {' '.join(cmd)}")
        logger.error(f"Error output: {e.stderr}")
        raise

def setup_test_environment():
    """Set up the test environment"""
    logger.info("Setting up test environment...")
    
    # Create test directories
    test_dirs = ['test_data/offers', 'test_data/invoices']
    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Generate test PDFs
    logger.info("Generating test PDFs...")
    run_command(['python', 'tools/generate_test_pdfs.py'])
    
    # Copy test PDFs to test directories
    for pdf_file in Path('test_pdfs').glob('*.pdf'):
        if 'offer' in pdf_file.name:
            shutil.copy2(pdf_file, 'test_data/offers/')
        elif 'invoice' in pdf_file.name:
            shutil.copy2(pdf_file, 'test_data/invoices/')

def run_quick_test():
    """Run a quick test of the tool"""
    logger.info("\nRunning quick test of PDF Comparison Tool...")
    
    # 1. Perfect Match Test
    logger.info("\n1. Testing Perfect Match Case...")
    run_command([
        'python', 'src/main.py',
        '--offer', 'test_data/offers/offer_perfect.pdf',
        '--invoice', 'test_data/invoices/invoice_perfect.pdf'
    ])
    input("\nPress Enter to continue to next test...")

    # 2. Quantity Mismatch Test
    logger.info("\n2. Testing Quantity Mismatch Case...")
    run_command([
        'python', 'src/main.py',
        '--offer', 'test_data/offers/offer_quantity_mismatch.pdf',
        '--invoice', 'test_data/invoices/invoice_quantity_mismatch.pdf'
    ])
    input("\nPress Enter to continue to next test...")

    # 3. Price Mismatch Test
    logger.info("\n3. Testing Price Mismatch Case...")
    run_command([
        'python', 'src/main.py',
        '--offer', 'test_data/offers/offer_price_mismatch.pdf',
        '--invoice', 'test_data/invoices/invoice_price_mismatch.pdf'
    ])
    input("\nPress Enter to continue to next test...")

    # 4. Missing Items Test
    logger.info("\n4. Testing Missing Items Case...")
    run_command([
        'python', 'src/main.py',
        '--offer', 'test_data/offers/offer_missing_items.pdf',
        '--invoice', 'test_data/invoices/invoice_missing_items.pdf'
    ])
    input("\nPress Enter to continue to next test...")

    # 5. Extra Items Test
    logger.info("\n5. Testing Extra Items Case...")
    run_command([
        'python', 'src/main.py',
        '--offer', 'test_data/offers/offer_extra_items.pdf',
        '--invoice', 'test_data/invoices/invoice_extra_items.pdf'
    ])
    input("\nPress Enter to continue to next test...")

    # 6. Partial Delivery Test
    logger.info("\n6. Testing Partial Delivery Case...")
    run_command([
        'python', 'src/main.py',
        '--offer', 'test_data/offers/offer_partial.pdf',
        '--invoice', 'test_data/invoices/invoice_partial_1.pdf',
        'test_data/invoices/invoice_partial_2.pdf'
    ])
    input("\nPress Enter to continue to GUI test...")

    # 7. GUI Test
    logger.info("\n7. Testing GUI Interface...")
    logger.info("Starting GUI application. Please:")
    logger.info("1. Drag and drop PDFs from test_data/offers and test_data/invoices")
    logger.info("2. Click 'Compare' to see results")
    logger.info("3. Close the application when done")
    
    run_command(['python', 'src/main.py'])

def test_monitoring():
    """Test file monitoring functionality"""
    logger.info("\nTesting file monitoring...")
    logger.info("Starting monitor mode. The tool will watch test_data folders.")
    logger.info("1. Copy offer_perfect.pdf to test_data/offers")
    logger.info("2. Copy invoice_perfect.pdf to test_data/invoices")
    logger.info("3. Watch the automatic comparison")
    logger.info("4. Press Ctrl+C to stop monitoring")
    
    try:
        run_command([
            'python', 'src/main.py',
            '--monitor',
            '--offers-dir', 'test_data/offers',
            '--invoices-dir', 'test_data/invoices'
        ])
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped")

def main():
    """Main entry point"""
    try:
        # Check if running from project root
        if not all(Path(f).exists() for f in ['src', 'tools', 'tests']):
            logger.error("Please run this script from the project root directory")
            return 1
        
        print("PDF Comparison Tool - Quick Test")
        print("===============================")
        print("\nThis script will:")
        print("1. Set up a test environment")
        print("2. Generate sample PDFs")
        print("3. Run comparisons with different scenarios")
        print("4. Test the GUI interface")
        print("5. Test file monitoring")
        
        input("\nPress Enter to begin testing...")
        
        # Setup
        setup_test_environment()
        
        # Run tests
        run_quick_test()
        
        # Test monitoring
        test_monitoring()
        
        print("\nQuick test completed successfully!")
        print("\nFor more detailed testing options, see TESTING.md")
        return 0
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
