from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

Base = declarative_base()

class ComparisonRecord(Base):
    """Model for storing comparison results"""
    __tablename__ = 'comparisons'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    offer_path = Column(String)
    invoice_paths = Column(String)  # JSON array of paths
    status = Column(String)  # 'success', 'error'
    error_message = Column(String, nullable=True)
    
    # Summary statistics
    total_items = Column(Integer)
    matches = Column(Integer)
    quantity_mismatches = Column(Integer)
    price_mismatches = Column(Integer)
    missing_items = Column(Integer)
    extra_items = Column(Integer)
    total_quantity_difference = Column(Float)
    total_price_difference = Column(Float)
    
    # Detailed results stored as JSON
    results = Column(JSON)
    
    # Notification status
    notification_sent = Column(Boolean, default=False)
    notification_error = Column(String, nullable=True)

class DatabaseManager:
    def __init__(self, db_path: str):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine and tables
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def store_comparison(self,
                        offer_path: str,
                        invoice_paths: List[str],
                        status: str,
                        summary: Dict,
                        results: List[Dict],
                        error_message: Optional[str] = None) -> int:
        """
        Store comparison results in database
        
        Args:
            offer_path: Path to offer PDF
            invoice_paths: List of paths to invoice PDFs
            status: Status of comparison ('success' or 'error')
            summary: Summary statistics
            results: Detailed comparison results
            error_message: Optional error message if status is 'error'
            
        Returns:
            int: ID of created record
        """
        try:
            session = self.Session()
            
            record = ComparisonRecord(
                offer_path=offer_path,
                invoice_paths=json.dumps(invoice_paths),
                status=status,
                error_message=error_message,
                
                # Summary statistics
                total_items=summary.get('total_items', 0),
                matches=summary.get('matches', 0),
                quantity_mismatches=summary.get('quantity_mismatches', 0),
                price_mismatches=summary.get('price_mismatches', 0),
                missing_items=summary.get('missing_items', 0),
                extra_items=summary.get('extra_items', 0),
                total_quantity_difference=float(summary.get('total_quantity_difference', 0)),
                total_price_difference=float(summary.get('total_price_difference', 0)),
                
                # Store detailed results as JSON
                results=json.dumps(results)
            )
            
            session.add(record)
            session.commit()
            
            record_id = record.id
            session.close()
            
            logging.info(f"Stored comparison record with ID {record_id}")
            return record_id
            
        except Exception as e:
            logging.error(f"Error storing comparison results: {str(e)}")
            if session:
                session.rollback()
                session.close()
            raise

    def update_notification_status(self,
                                 record_id: int,
                                 sent: bool,
                                 error: Optional[str] = None) -> bool:
        """
        Update notification status for a comparison record
        
        Args:
            record_id: ID of comparison record
            sent: Whether notification was sent successfully
            error: Optional error message if notification failed
            
        Returns:
            bool: True if update was successful
        """
        try:
            session = self.Session()
            
            record = session.query(ComparisonRecord).get(record_id)
            if record:
                record.notification_sent = sent
                record.notification_error = error
                session.commit()
                session.close()
                return True
            
            session.close()
            return False
            
        except Exception as e:
            logging.error(f"Error updating notification status: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False

    def get_comparison_history(self,
                             days: Optional[int] = None,
                             limit: Optional[int] = None) -> List[Dict]:
        """
        Get comparison history
        
        Args:
            days: Optional number of days to look back
            limit: Optional maximum number of records to return
            
        Returns:
            List of comparison records as dictionaries
        """
        try:
            session = self.Session()
            
            query = session.query(ComparisonRecord)
            
            if days:
                cutoff = datetime.utcnow() - timedelta(days=days)
                query = query.filter(ComparisonRecord.timestamp >= cutoff)
            
            query = query.order_by(ComparisonRecord.timestamp.desc())
            
            if limit:
                query = query.limit(limit)
            
            records = query.all()
            
            # Convert to dictionaries
            results = []
            for record in records:
                results.append({
                    'id': record.id,
                    'timestamp': record.timestamp.isoformat(),
                    'offer_path': record.offer_path,
                    'invoice_paths': json.loads(record.invoice_paths),
                    'status': record.status,
                    'error_message': record.error_message,
                    'summary': {
                        'total_items': record.total_items,
                        'matches': record.matches,
                        'quantity_mismatches': record.quantity_mismatches,
                        'price_mismatches': record.price_mismatches,
                        'missing_items': record.missing_items,
                        'extra_items': record.extra_items,
                        'total_quantity_difference': record.total_quantity_difference,
                        'total_price_difference': record.total_price_difference
                    },
                    'results': json.loads(record.results),
                    'notification_sent': record.notification_sent,
                    'notification_error': record.notification_error
                })
            
            session.close()
            return results
            
        except Exception as e:
            logging.error(f"Error retrieving comparison history: {str(e)}")
            if session:
                session.close()
            return []

    def cleanup_old_records(self, days: int) -> int:
        """
        Delete records older than specified number of days
        
        Args:
            days: Number of days to keep records for
            
        Returns:
            int: Number of records deleted
        """
        try:
            session = self.Session()
            
            cutoff = datetime.utcnow() - timedelta(days=days)
            deleted = session.query(ComparisonRecord)\
                           .filter(ComparisonRecord.timestamp < cutoff)\
                           .delete()
            
            session.commit()
            session.close()
            
            logging.info(f"Deleted {deleted} old comparison records")
            return deleted
            
        except Exception as e:
            logging.error(f"Error cleaning up old records: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return 0

    def get_statistics(self, days: Optional[int] = None) -> Dict:
        """
        Get statistics about comparisons
        
        Args:
            days: Optional number of days to look back
            
        Returns:
            Dictionary with statistics
        """
        try:
            session = self.Session()
            
            query = session.query(ComparisonRecord)
            
            if days:
                cutoff = datetime.utcnow() - timedelta(days=days)
                query = query.filter(ComparisonRecord.timestamp >= cutoff)
            
            records = query.all()
            
            stats = {
                'total_comparisons': len(records),
                'successful_comparisons': 0,
                'failed_comparisons': 0,
                'total_items_compared': 0,
                'total_matches': 0,
                'total_quantity_mismatches': 0,
                'total_price_mismatches': 0,
                'total_missing_items': 0,
                'total_extra_items': 0,
                'total_quantity_difference': 0,
                'total_price_difference': 0,
                'notifications': {
                    'sent': 0,
                    'failed': 0
                }
            }
            
            for record in records:
                if record.status == 'success':
                    stats['successful_comparisons'] += 1
                else:
                    stats['failed_comparisons'] += 1
                
                stats['total_items_compared'] += record.total_items
                stats['total_matches'] += record.matches
                stats['total_quantity_mismatches'] += record.quantity_mismatches
                stats['total_price_mismatches'] += record.price_mismatches
                stats['total_missing_items'] += record.missing_items
                stats['total_extra_items'] += record.extra_items
                stats['total_quantity_difference'] += record.total_quantity_difference
                stats['total_price_difference'] += record.total_price_difference
                
                if record.notification_sent:
                    stats['notifications']['sent'] += 1
                elif record.notification_error:
                    stats['notifications']['failed'] += 1
            
            session.close()
            return stats
            
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            if session:
                session.close()
            return {}
