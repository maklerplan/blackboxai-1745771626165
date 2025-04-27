import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from src.database import DatabaseManager, ComparisonRecord

@pytest.fixture
def temp_db():
    """Create a temporary database file"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
        yield db_path
        # Clean up
        Path(db_path).unlink()

@pytest.fixture
def db_manager(temp_db):
    """Create a DatabaseManager instance with temporary database"""
    return DatabaseManager(temp_db)

@pytest.fixture
def sample_comparison_data():
    """Create sample comparison data"""
    return {
        'offer_path': '/test/offers/offer.pdf',
        'invoice_paths': ['/test/invoices/invoice1.pdf', '/test/invoices/invoice2.pdf'],
        'status': 'success',
        'summary': {
            'total_items': 3,
            'matches': 1,
            'quantity_mismatches': 1,
            'price_mismatches': 1,
            'missing_items': 0,
            'extra_items': 0,
            'total_quantity_difference': Decimal('2'),
            'total_price_difference': Decimal('25.50')
        },
        'results': [
            {
                'item_code': 'A123',
                'description': 'Test Item 1',
                'status': 'match',
                'offer_quantity': Decimal('10'),
                'delivered_quantity': Decimal('10'),
                'offer_price': Decimal('15.50'),
                'invoiced_price': Decimal('15.50'),
                'quantity_difference': Decimal('0'),
                'price_difference': Decimal('0')
            },
            {
                'item_code': 'B456',
                'description': 'Test Item 2',
                'status': 'quantity_mismatch',
                'offer_quantity': Decimal('5'),
                'delivered_quantity': Decimal('3'),
                'offer_price': Decimal('25.00'),
                'invoiced_price': Decimal('25.00'),
                'quantity_difference': Decimal('2'),
                'price_difference': Decimal('0')
            },
            {
                'item_code': 'C789',
                'description': 'Test Item 3',
                'status': 'price_mismatch',
                'offer_quantity': Decimal('2'),
                'delivered_quantity': Decimal('2'),
                'offer_price': Decimal('50.00'),
                'invoiced_price': Decimal('62.75'),
                'quantity_difference': Decimal('0'),
                'price_difference': Decimal('-25.50')
            }
        ]
    }

def test_database_initialization(temp_db):
    """Test database initialization"""
    db_manager = DatabaseManager(temp_db)
    assert Path(temp_db).exists()

def test_store_comparison(db_manager, sample_comparison_data):
    """Test storing comparison results"""
    record_id = db_manager.store_comparison(
        offer_path=sample_comparison_data['offer_path'],
        invoice_paths=sample_comparison_data['invoice_paths'],
        status=sample_comparison_data['status'],
        summary=sample_comparison_data['summary'],
        results=sample_comparison_data['results']
    )
    
    assert record_id > 0
    
    # Verify record was stored
    session = db_manager.Session()
    record = session.query(ComparisonRecord).get(record_id)
    
    assert record is not None
    assert record.offer_path == sample_comparison_data['offer_path']
    assert record.total_items == sample_comparison_data['summary']['total_items']
    assert record.matches == sample_comparison_data['summary']['matches']
    
    session.close()

def test_update_notification_status(db_manager, sample_comparison_data):
    """Test updating notification status"""
    # Store a record
    record_id = db_manager.store_comparison(
        offer_path=sample_comparison_data['offer_path'],
        invoice_paths=sample_comparison_data['invoice_paths'],
        status=sample_comparison_data['status'],
        summary=sample_comparison_data['summary'],
        results=sample_comparison_data['results']
    )
    
    # Update notification status
    success = db_manager.update_notification_status(
        record_id=record_id,
        sent=True,
        error=None
    )
    
    assert success
    
    # Verify update
    session = db_manager.Session()
    record = session.query(ComparisonRecord).get(record_id)
    
    assert record.notification_sent is True
    assert record.notification_error is None
    
    session.close()

def test_get_comparison_history(db_manager, sample_comparison_data):
    """Test retrieving comparison history"""
    # Store multiple records
    for _ in range(3):
        db_manager.store_comparison(
            offer_path=sample_comparison_data['offer_path'],
            invoice_paths=sample_comparison_data['invoice_paths'],
            status=sample_comparison_data['status'],
            summary=sample_comparison_data['summary'],
            results=sample_comparison_data['results']
        )
    
    # Get history
    history = db_manager.get_comparison_history(days=1)
    
    assert len(history) == 3
    
    # Verify record structure
    record = history[0]
    assert 'id' in record
    assert 'timestamp' in record
    assert 'offer_path' in record
    assert 'invoice_paths' in record
    assert 'summary' in record
    assert 'results' in record

def test_cleanup_old_records(db_manager, sample_comparison_data):
    """Test cleaning up old records"""
    # Store records with different timestamps
    session = db_manager.Session()
    
    # Old record
    old_record = ComparisonRecord(
        timestamp=datetime.utcnow() - timedelta(days=10),
        offer_path=sample_comparison_data['offer_path'],
        invoice_paths=str(sample_comparison_data['invoice_paths']),
        status=sample_comparison_data['status'],
        total_items=sample_comparison_data['summary']['total_items'],
        matches=sample_comparison_data['summary']['matches'],
        quantity_mismatches=sample_comparison_data['summary']['quantity_mismatches'],
        price_mismatches=sample_comparison_data['summary']['price_mismatches'],
        missing_items=sample_comparison_data['summary']['missing_items'],
        extra_items=sample_comparison_data['summary']['extra_items'],
        total_quantity_difference=float(sample_comparison_data['summary']['total_quantity_difference']),
        total_price_difference=float(sample_comparison_data['summary']['total_price_difference']),
        results=str(sample_comparison_data['results'])
    )
    
    # Recent record
    recent_record = ComparisonRecord(
        timestamp=datetime.utcnow(),
        offer_path=sample_comparison_data['offer_path'],
        invoice_paths=str(sample_comparison_data['invoice_paths']),
        status=sample_comparison_data['status'],
        total_items=sample_comparison_data['summary']['total_items'],
        matches=sample_comparison_data['summary']['matches'],
        quantity_mismatches=sample_comparison_data['summary']['quantity_mismatches'],
        price_mismatches=sample_comparison_data['summary']['price_mismatches'],
        missing_items=sample_comparison_data['summary']['missing_items'],
        extra_items=sample_comparison_data['summary']['extra_items'],
        total_quantity_difference=float(sample_comparison_data['summary']['total_quantity_difference']),
        total_price_difference=float(sample_comparison_data['summary']['total_price_difference']),
        results=str(sample_comparison_data['results'])
    )
    
    session.add(old_record)
    session.add(recent_record)
    session.commit()
    session.close()
    
    # Clean up records older than 7 days
    deleted = db_manager.cleanup_old_records(days=7)
    
    assert deleted == 1
    
    # Verify only recent record remains
    history = db_manager.get_comparison_history()
    assert len(history) == 1
    assert (datetime.fromisoformat(history[0]['timestamp']) - datetime.utcnow()).days == 0

def test_get_statistics(db_manager, sample_comparison_data):
    """Test getting comparison statistics"""
    # Store some records with different statuses
    db_manager.store_comparison(
        offer_path=sample_comparison_data['offer_path'],
        invoice_paths=sample_comparison_data['invoice_paths'],
        status='success',
        summary=sample_comparison_data['summary'],
        results=sample_comparison_data['results']
    )
    
    # Store a failed comparison
    db_manager.store_comparison(
        offer_path=sample_comparison_data['offer_path'],
        invoice_paths=sample_comparison_data['invoice_paths'],
        status='error',
        summary={'total_items': 0, 'matches': 0},
        results=[],
        error_message='Test error'
    )
    
    # Get statistics
    stats = db_manager.get_statistics(days=1)
    
    assert stats['total_comparisons'] == 2
    assert stats['successful_comparisons'] == 1
    assert stats['failed_comparisons'] == 1
    assert stats['total_items_compared'] == sample_comparison_data['summary']['total_items']
    assert stats['total_matches'] == sample_comparison_data['summary']['matches']
    assert stats['total_quantity_mismatches'] == sample_comparison_data['summary']['quantity_mismatches']
    assert stats['total_price_mismatches'] == sample_comparison_data['summary']['price_mismatches']

def test_error_handling(db_manager, sample_comparison_data):
    """Test error handling in database operations"""
    # Test with invalid record ID
    success = db_manager.update_notification_status(
        record_id=999999,
        sent=True
    )
    assert not success
    
    # Test with invalid data types
    with pytest.raises(Exception):
        db_manager.store_comparison(
            offer_path=123,  # Invalid type
            invoice_paths=sample_comparison_data['invoice_paths'],
            status=sample_comparison_data['status'],
            summary=sample_comparison_data['summary'],
            results=sample_comparison_data['results']
        )

if __name__ == '__main__':
    pytest.main([__file__])
