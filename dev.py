#!/usr/bin/env python3
"""
Development helper script for PDF Comparison Tool.
Provides commands for common development tasks.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
import shutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_app(args):
    """Run the application"""
    try:
        cmd = ['python', 'src/main.py']
        if args.debug:
            cmd.append('--debug')
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Error running application: {str(e)}")
        return 1
    return 0

def run_tests(args):
    """Run tests with specified options"""
    try:
        cmd = ['python', 'run_tests.py']
        if args.coverage:
            cmd.append('--coverage')
        if args.html:
            cmd.append('--html')
        if args.verbose:
            cmd.append('--verbose')
        if args.failfast:
            cmd.append('--failfast')
        if args.file:
            cmd.extend(['--file', args.file])
        
        subprocess.run(cmd)
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        return 1
    return 0

def clean(args):
    """Clean up generated files and directories"""
    patterns = [
        '**/__pycache__',
        '**/*.pyc',
        '**/*.pyo',
        '**/*.pyd',
        '**/.pytest_cache',
        '**/.coverage',
        '**/htmlcov',
        'build/',
        'dist/',
        '**/*.egg-info',
    ]
    
    if args.all:
        patterns.extend([
            'venv/',
            'logs/*.log',
            'data/*.db'
        ])
    
    count = 0
    for pattern in patterns:
        for path in Path('.').glob(pattern):
            try:
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                count += 1
                logger.info(f"Removed: {path}")
            except Exception as e:
                logger.error(f"Error removing {path}: {str(e)}")
    
    logger.info(f"Cleaned up {count} items")
    return 0

def setup_dev(args):
    """Set up development environment"""
    try:
        # Create virtual environment if it doesn't exist
        if not Path('venv').exists():
            logger.info("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'])
        
        # Activate virtual environment
        if os.name == 'nt':  # Windows
            activate_script = 'venv\\Scripts\\activate'
        else:  # Unix
            activate_script = 'source venv/bin/activate'
        
        # Install dependencies
        logger.info("Installing dependencies...")
        pip_cmd = 'pip install -r requirements.txt'
        subprocess.run(f"{activate_script} && {pip_cmd}", shell=True)
        
        # Create necessary directories
        for dir_name in ['data', 'logs']:
            Path(dir_name).mkdir(exist_ok=True)
        
        # Create configuration file if it doesn't exist
        if not Path('config/settings.yaml').exists():
            shutil.copy('config/settings.yaml.example', 'config/settings.yaml')
            logger.info("Created configuration file from example")
        
        logger.info("Development environment setup complete")
        return 0
    except Exception as e:
        logger.error(f"Error setting up development environment: {str(e)}")
        return 1

def create_backup(args):
    """Create a backup of important files"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path(f'backups/backup_{timestamp}')
        backup_dir.mkdir(parents=True)
        
        # Files to backup
        backup_paths = [
            'src/',
            'tests/',
            'config/',
            'requirements.txt',
            'setup.sh',
            'setup.bat'
        ]
        
        if args.include_data:
            backup_paths.extend([
                'data/',
                'logs/'
            ])
        
        for path in backup_paths:
            src_path = Path(path)
            if src_path.exists():
                dst_path = backup_dir / path
                if src_path.is_dir():
                    shutil.copytree(src_path, dst_path)
                else:
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
        
        logger.info(f"Backup created at: {backup_dir}")
        return 0
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        return 1

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='PDF Comparison Tool Development Helper')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the application')
    run_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    test_parser.add_argument('--html', action='store_true', help='Generate HTML coverage report')
    test_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    test_parser.add_argument('--failfast', action='store_true', help='Stop on first failure')
    test_parser.add_argument('--file', '-f', help='Run specific test file')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean up generated files')
    clean_parser.add_argument('--all', action='store_true', help='Clean everything including venv and data')
    
    # Setup command
    subparsers.add_parser('setup', help='Set up development environment')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup')
    backup_parser.add_argument('--include-data', action='store_true', help='Include data and log files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'run':
        return run_app(args)
    elif args.command == 'test':
        return run_tests(args)
    elif args.command == 'clean':
        return clean(args)
    elif args.command == 'setup':
        return setup_dev(args)
    elif args.command == 'backup':
        return create_backup(args)

if __name__ == "__main__":
    sys.exit(main())
