#!/usr/bin/env python3
"""
Maintenance script for PDF Comparison Tool.
Handles routine maintenance tasks like cleaning up old logs and database records.
"""

import sys
import os
from pathlib import Path
import logging
import shutil
from datetime import datetime, timedelta
import yaml
import argparse
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Maintenance:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return {}

    def cleanup_logs(self, days: int = None) -> int:
        """
        Clean up old log files
        
        Args:
            days: Number of days to keep logs for (overrides config)
            
        Returns:
            int: Number of files deleted
        """
        try:
            if not days:
                days = self.config.get('logging', {}).get('retention_days', 30)
            
            log_dir = Path(self.config.get('logging', {}).get('file', 'logs/comparison_tool.log')).parent
            if not log_dir.exists():
                logger.warning(f"Log directory not found: {log_dir}")
                return 0
            
            cutoff = datetime.now() - timedelta(days=days)
            count = 0
            
            for log_file in log_dir.glob('*.log*'):
                if log_file.stat().st_mtime < cutoff.timestamp():
                    log_file.unlink()
                    count += 1
                    logger.info(f"Deleted old log file: {log_file}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up logs: {str(e)}")
            return 0

    def cleanup_database(self, days: int = None) -> int:
        """
        Clean up old database records
        
        Args:
            days: Number of days to keep records for (overrides config)
            
        Returns:
            int: Number of records deleted
        """
        try:
            if not days:
                days = self.config.get('database', {}).get('retention_days', 90)
            
            db_path = self.config.get('database', {}).get('path', 'data/comparison_history.db')
            if not Path(db_path).exists():
                logger.warning(f"Database not found: {db_path}")
                return 0
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Delete old records
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "DELETE FROM comparisons WHERE timestamp < ?",
                (cutoff,)
            )
            
            count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted {count} old database records")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up database: {str(e)}")
            return 0

    def optimize_database(self) -> bool:
        """
        Optimize the database (VACUUM)
        
        Returns:
            bool: True if successful
        """
        try:
            db_path = self.config.get('database', {}).get('path', 'data/comparison_history.db')
            if not Path(db_path).exists():
                logger.warning(f"Database not found: {db_path}")
                return False
            
            conn = sqlite3.connect(db_path)
            conn.execute("VACUUM")
            conn.close()
            
            logger.info("Database optimized")
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing database: {str(e)}")
            return False

    def backup_database(self, backup_dir: str = "backups") -> bool:
        """
        Create a backup of the database
        
        Args:
            backup_dir: Directory to store backups
            
        Returns:
            bool: True if successful
        """
        try:
            db_path = Path(self.config.get('database', {}).get('path', 'data/comparison_history.db'))
            if not db_path.exists():
                logger.warning(f"Database not found: {db_path}")
                return False
            
            # Create backup directory
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Create backup with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_path / f"comparison_history_{timestamp}.db"
            
            shutil.copy2(db_path, backup_file)
            logger.info(f"Database backed up to: {backup_file}")
            
            # Clean up old backups (keep last 5)
            backups = sorted(backup_path.glob('*.db'))
            for old_backup in backups[:-5]:
                old_backup.unlink()
                logger.info(f"Deleted old backup: {old_backup}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            return False

    def check_disk_space(self, min_free_mb: int = 1000) -> bool:
        """
        Check if there's enough disk space
        
        Args:
            min_free_mb: Minimum free space required in MB
            
        Returns:
            bool: True if enough space available
        """
        try:
            # Check data directory
            data_path = Path(self.config.get('database', {}).get('path', 'data/comparison_history.db')).parent
            if not data_path.exists():
                data_path.mkdir(parents=True)
            
            total, used, free = shutil.disk_usage(data_path)
            free_mb = free // (1024 * 1024)  # Convert to MB
            
            if free_mb < min_free_mb:
                logger.warning(f"Low disk space: {free_mb}MB free, {min_free_mb}MB required")
                return False
            
            logger.info(f"Disk space OK: {free_mb}MB free")
            return True
            
        except Exception as e:
            logger.error(f"Error checking disk space: {str(e)}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='PDF Comparison Tool Maintenance')
    parser.add_argument('--logs', type=int, help='Clean up logs older than N days')
    parser.add_argument('--database', type=int, help='Clean up database records older than N days')
    parser.add_argument('--optimize', action='store_true', help='Optimize database')
    parser.add_argument('--backup', action='store_true', help='Backup database')
    parser.add_argument('--check-space', action='store_true', help='Check disk space')
    parser.add_argument('--all', action='store_true', help='Run all maintenance tasks')
    
    args = parser.parse_args()
    
    maintenance = Maintenance()
    success = True
    
    if args.all or args.logs:
        logger.info("\nCleaning up logs...")
        count = maintenance.cleanup_logs(args.logs)
        logger.info(f"Deleted {count} old log files")
    
    if args.all or args.database:
        logger.info("\nCleaning up database...")
        count = maintenance.cleanup_database(args.database)
        logger.info(f"Deleted {count} old database records")
    
    if args.all or args.optimize:
        logger.info("\nOptimizing database...")
        if not maintenance.optimize_database():
            success = False
    
    if args.all or args.backup:
        logger.info("\nBacking up database...")
        if not maintenance.backup_database():
            success = False
    
    if args.all or args.check_space:
        logger.info("\nChecking disk space...")
        if not maintenance.check_disk_space():
            success = False
    
    if not any(vars(args).values()):
        parser.print_help()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
