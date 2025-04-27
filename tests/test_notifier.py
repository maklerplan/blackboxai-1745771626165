import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from src.notifier import SlackNotifier, NotificationConfig
from datetime import datetime

@pytest.fixture
def mock_config():
    """Create a mock notification configuration"""
    return NotificationConfig(
        webhook_url='https://hooks.slack.com/test',
        channel='#test-channel',
        notify_price_discrepancies=True,
        notify_quantity_mismatches=True,
        notify_missing_items=True,
        notify_successful_comparisons=False,
        price_threshold=Decimal('1.0'),
        quantity_threshold=1
    )

@pytest.fixture
def notifier(mock_config):
    """Create a SlackNotifier instance with mock configuration"""
    return SlackNotifier(mock_config)

@pytest.fixture
def sample_comparison_results():
    """Create sample comparison results"""
    return [
        {
            'item_code': 'A123',
            'description': 'Test Item 1',
            'status': 'quantity_mismatch',
            'offer_quantity': Decimal('10'),
            'delivered_quantity': Decimal('8'),
            'offer_price': Decimal('15.50'),
            'invoiced_price': Decimal('15.50'),
            'quantity_difference': Decimal('2'),
            'price_difference': Decimal('0')
        },
        {
            'item_code': 'B456',
            'description': 'Test Item 2',
            'status': 'price_mismatch',
            'offer_quantity': Decimal('5'),
            'delivered_quantity': Decimal('5'),
            'offer_price': Decimal('25.00'),
            'invoiced_price': Decimal('27.50'),
            'quantity_difference': Decimal('0'),
            'price_difference': Decimal('-2.50')
        },
        {
            'item_code': 'C789',
            'description': 'Test Item 3',
            'status': 'missing',
            'offer_quantity': Decimal('2'),
            'delivered_quantity': Decimal('0'),
            'offer_price': Decimal('50.00'),
            'invoiced_price': Decimal('0'),
            'quantity_difference': Decimal('2'),
            'price_difference': Decimal('50.00')
        }
    ]

@pytest.fixture
def sample_summary():
    """Create a sample comparison summary"""
    return {
        'total_items': 3,
        'matches': 0,
        'quantity_mismatches': 1,
        'price_mismatches': 1,
        'missing_items': 1,
        'extra_items': 0,
        'total_quantity_difference': Decimal('4'),
        'total_price_difference': Decimal('52.50')
    }

def test_should_send_notification(notifier, sample_summary):
    """Test notification trigger conditions"""
    # Should notify for quantity mismatches
    assert notifier._should_send_notification({
        **sample_summary,
        'quantity_mismatches': 1,
        'price_mismatches': 0,
        'missing_items': 0
    })
    
    # Should notify for price discrepancies
    assert notifier._should_send_notification({
        **sample_summary,
        'quantity_mismatches': 0,
        'price_mismatches': 1,
        'missing_items': 0
    })
    
    # Should notify for missing items
    assert notifier._should_send_notification({
        **sample_summary,
        'quantity_mismatches': 0,
        'price_mismatches': 0,
        'missing_items': 1
    })
    
    # Should not notify for successful comparison by default
    assert not notifier._should_send_notification({
        **sample_summary,
        'matches': 3,
        'quantity_mismatches': 0,
        'price_mismatches': 0,
        'missing_items': 0,
        'total_items': 3
    })

def test_create_message_blocks(notifier, sample_comparison_results, sample_summary):
    """Test creation of Slack message blocks"""
    offer_path = '/test/offers/offer.pdf'
    invoice_paths = ['/test/invoices/invoice1.pdf', '/test/invoices/invoice2.pdf']
    
    blocks = notifier._create_message_blocks(
        offer_path,
        invoice_paths,
        sample_comparison_results,
        sample_summary
    )
    
    # Verify basic structure
    assert isinstance(blocks, list)
    assert len(blocks) > 0
    
    # Check header
    assert blocks[0]['type'] == 'header'
    assert 'PDF Comparison Results' in blocks[0]['text']['text']
    
    # Check files section
    files_block = next(b for b in blocks if b['type'] == 'section' and 'Offer:' in b['text']['text'])
    assert 'offer.pdf' in files_block['text']['text']
    assert 'invoice1.pdf' in files_block['text']['text']
    assert 'invoice2.pdf' in files_block['text']['text']
    
    # Check summary section
    summary_block = next(b for b in blocks if b['type'] == 'section' and 'Summary' in b['text']['text'])
    summary_text = summary_block['text']['text']
    assert 'Total Items: 3' in summary_text
    assert 'Quantity Mismatches: 1' in summary_text
    assert 'Price Mismatches: 1' in summary_text
    assert 'Missing Items: 1' in summary_text

def test_format_discrepancy(notifier):
    """Test formatting of individual discrepancies"""
    # Test quantity mismatch
    quantity_mismatch = {
        'item_code': 'A123',
        'description': 'Test Item',
        'status': 'quantity_mismatch',
        'offer_quantity': Decimal('10'),
        'delivered_quantity': Decimal('8'),
        'quantity_difference': Decimal('2')
    }
    text = notifier._format_discrepancy(quantity_mismatch)
    assert 'A123' in text
    assert 'Test Item' in text
    assert '10' in text
    assert '8' in text
    assert '2' in text
    
    # Test price mismatch
    price_mismatch = {
        'item_code': 'B456',
        'description': 'Test Item',
        'status': 'price_mismatch',
        'offer_price': Decimal('25.00'),
        'invoiced_price': Decimal('27.50'),
        'price_difference': Decimal('-2.50')
    }
    text = notifier._format_discrepancy(price_mismatch)
    assert 'B456' in text
    assert '25.00' in text
    assert '27.50' in text
    assert '2.50' in text

@patch('requests.Session')
def test_send_comparison_results(mock_session, notifier, sample_comparison_results, sample_summary):
    """Test sending comparison results to Slack"""
    # Mock the POST response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_session.return_value.post.return_value = mock_response
    
    result = notifier.send_comparison_results(
        offer_path='/test/offers/offer.pdf',
        invoice_paths=['/test/invoices/invoice.pdf'],
        results=sample_comparison_results,
        summary=sample_summary
    )
    
    assert result is True
    mock_session.return_value.post.assert_called_once()
    
    # Verify the call arguments
    call_args = mock_session.return_value.post.call_args
    assert call_args[0][0] == 'https://hooks.slack.com/test'
    assert 'blocks' in call_args[1]['json']

@patch('requests.Session')
def test_send_error(mock_session, notifier):
    """Test sending error notifications"""
    # Mock the POST response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_session.return_value.post.return_value = mock_response
    
    result = notifier.send_error(
        error_message="Test error",
        details="Detailed error information"
    )
    
    assert result is True
    mock_session.return_value.post.assert_called_once()
    
    # Verify the call arguments
    call_args = mock_session.return_value.post.call_args
    assert call_args[0][0] == 'https://hooks.slack.com/test'
    
    blocks = call_args[1]['json']['blocks']
    assert any('Test error' in b['text']['text'] for b in blocks if b['type'] == 'section')
    assert any('Detailed error information' in b['text']['text'] for b in blocks if b['type'] == 'section')

@patch('requests.Session')
def test_failed_notification(mock_session, notifier, sample_comparison_results, sample_summary):
    """Test handling of failed notifications"""
    # Mock a failed POST response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_session.return_value.post.return_value = mock_response
    
    result = notifier.send_comparison_results(
        offer_path='/test/offers/offer.pdf',
        invoice_paths=['/test/invoices/invoice.pdf'],
        results=sample_comparison_results,
        summary=sample_summary
    )
    
    assert result is False

def test_notification_thresholds(notifier, sample_summary):
    """Test notification thresholds"""
    # Modify config to set thresholds
    notifier.config.price_threshold = Decimal('5.0')
    notifier.config.quantity_threshold = 5
    
    # Should not notify for small differences
    small_differences = {
        **sample_summary,
        'total_quantity_difference': Decimal('3'),
        'total_price_difference': Decimal('4.0')
    }
    assert not notifier._should_send_notification(small_differences)
    
    # Should notify for differences above threshold
    large_differences = {
        **sample_summary,
        'total_quantity_difference': Decimal('6'),
        'total_price_difference': Decimal('6.0')
    }
    assert notifier._should_send_notification(large_differences)

if __name__ == '__main__':
    pytest.main([__file__])
