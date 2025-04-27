import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
from src.file_monitor import PDFEventHandler, FolderMonitor, AutoProcessor

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def mock_callback():
    """Create a mock callback function"""
    return Mock()

@pytest.fixture
def event_handler(mock_callback):
    """Create a PDFEventHandler instance"""
    return PDFEventHandler(mock_callback, 'test')

@pytest.fixture
def folder_monitor():
    """Create a FolderMonitor instance"""
    return FolderMonitor()

@pytest.fixture
def auto_processor(folder_monitor, mock_callback):
    """Create an AutoProcessor instance"""
    return AutoProcessor(folder_monitor, mock_callback)

def create_pdf_file(directory: str, filename: str) -> Path:
    """Create a dummy PDF file"""
    file_path = Path(directory) / filename
    file_path.write_bytes(b'%PDF-1.4\n%Test PDF content')
    return file_path

def test_pdf_event_handler_creation(event_handler):
    """Test PDFEventHandler initialization"""
    assert event_handler.callback is not None
    assert event_handler.file_type == 'test'
    assert isinstance(event_handler.processed_files, set)
    assert event_handler.processing_queue is not None

def test_pdf_event_handler_file_detection(event_handler, temp_dir):
    """Test PDF file detection"""
    # Create a PDF file
    pdf_path = create_pdf_file(temp_dir, 'test.pdf')
    
    # Simulate file creation event
    class Event:
        is_directory = False
        src_path = str(pdf_path)
    
    event_handler.on_created(Event())
    
    # Wait for processing
    time.sleep(2)
    
    # Verify callback was called
    event_handler.callback.assert_called_once_with(str(pdf_path))

def test_pdf_event_handler_non_pdf_ignore(event_handler, temp_dir):
    """Test non-PDF file handling"""
    # Create a non-PDF file
    txt_path = Path(temp_dir) / 'test.txt'
    txt_path.write_text('Test content')
    
    # Simulate file creation event
    class Event:
        is_directory = False
        src_path = str(txt_path)
    
    event_handler.on_created(Event())
    
    # Verify callback was not called
    event_handler.callback.assert_not_called()

def test_folder_monitor_start_stop(folder_monitor, temp_dir, mock_callback):
    """Test starting and stopping folder monitoring"""
    offers_path = Path(temp_dir) / 'offers'
    invoices_path = Path(temp_dir) / 'invoices'
    offers_path.mkdir()
    invoices_path.mkdir()
    
    # Start monitoring
    folder_monitor.start_monitoring(
        str(offers_path),
        str(invoices_path),
        mock_callback,
        mock_callback
    )
    
    assert folder_monitor.is_monitoring()
    
    # Stop monitoring
    folder_monitor.stop_monitoring()
    assert not folder_monitor.is_monitoring()

@patch('watchdog.observers.Observer')
def test_folder_monitor_file_handling(mock_observer, folder_monitor, temp_dir, mock_callback):
    """Test folder monitor's file handling"""
    offers_path = Path(temp_dir) / 'offers'
    invoices_path = Path(temp_dir) / 'invoices'
    offers_path.mkdir()
    invoices_path.mkdir()
    
    # Start monitoring
    folder_monitor.start_monitoring(
        str(offers_path),
        str(invoices_path),
        mock_callback,
        mock_callback
    )
    
    # Verify observer was started
    mock_observer.return_value.start.assert_called_once()
    
    # Verify handlers were scheduled
    assert len(folder_monitor.handlers) == 2
    assert 'offer' in folder_monitor.handlers
    assert 'invoice' in folder_monitor.handlers

def test_auto_processor_offer_handling(auto_processor, temp_dir):
    """Test AutoProcessor offer handling"""
    # Create an offer PDF
    offer_path = create_pdf_file(temp_dir, 'offer.pdf')
    
    # Process the offer
    auto_processor.handle_offer(str(offer_path))
    
    # Verify offer is pending
    assert str(offer_path) in auto_processor.pending_offers

def test_auto_processor_invoice_handling(auto_processor, temp_dir):
    """Test AutoProcessor invoice handling"""
    # Create offer and invoice PDFs
    offer_path = create_pdf_file(temp_dir, 'offer.pdf')
    invoice_path = create_pdf_file(temp_dir, 'invoice.pdf')
    
    # Add offer to pending
    auto_processor.handle_offer(str(offer_path))
    
    # Process invoice
    auto_processor.handle_invoice(str(invoice_path))
    
    # Verify comparison was triggered
    auto_processor.comparison_callback.assert_called_with(
        str(offer_path),
        [str(invoice_path)]
    )

def test_auto_processor_cleanup(auto_processor, temp_dir):
    """Test cleanup of old pending offers"""
    # Create an offer PDF
    offer_path = create_pdf_file(temp_dir, 'offer.pdf')
    
    # Add offer with old timestamp
    with patch('datetime.datetime') as mock_datetime:
        # Set current time to past
        mock_datetime.now.return_value = mock_datetime.now.return_value.replace(
            day=mock_datetime.now.return_value.day - 2
        )
        auto_processor.handle_offer(str(offer_path))
    
    # Wait for cleanup
    time.sleep(2)
    
    # Verify offer was removed
    assert str(offer_path) not in auto_processor.pending_offers

def test_multiple_invoice_handling(auto_processor, temp_dir):
    """Test handling multiple invoices for one offer"""
    # Create PDFs
    offer_path = create_pdf_file(temp_dir, 'offer.pdf')
    invoice1_path = create_pdf_file(temp_dir, 'invoice1.pdf')
    invoice2_path = create_pdf_file(temp_dir, 'invoice2.pdf')
    
    # Process offer and invoices
    auto_processor.handle_offer(str(offer_path))
    auto_processor.handle_invoice(str(invoice1_path))
    auto_processor.handle_invoice(str(invoice2_path))
    
    # Verify comparisons were triggered
    assert auto_processor.comparison_callback.call_count == 2
    
    # Verify each invoice was compared with the offer
    auto_processor.comparison_callback.assert_any_call(
        str(offer_path),
        [str(invoice1_path)]
    )
    auto_processor.comparison_callback.assert_any_call(
        str(offer_path),
        [str(invoice2_path)]
    )

def test_duplicate_file_handling(event_handler, temp_dir):
    """Test handling of duplicate file events"""
    # Create a PDF file
    pdf_path = create_pdf_file(temp_dir, 'test.pdf')
    
    # Simulate multiple events for the same file
    class Event:
        is_directory = False
        src_path = str(pdf_path)
    
    # Trigger multiple events
    event_handler.on_created(Event())
    event_handler.on_modified(Event())
    event_handler.on_created(Event())
    
    # Wait for processing
    time.sleep(2)
    
    # Verify callback was called only once
    assert event_handler.callback.call_count == 1

def test_error_handling(event_handler, temp_dir):
    """Test error handling in file processing"""
    # Create a mock callback that raises an exception
    event_handler.callback = Mock(side_effect=Exception("Test error"))
    
    # Create a PDF file
    pdf_path = create_pdf_file(temp_dir, 'test.pdf')
    
    # Simulate file creation event
    class Event:
        is_directory = False
        src_path = str(pdf_path)
    
    # This should not raise an exception
    event_handler.on_created(Event())
    
    # Wait for processing
    time.sleep(2)
    
    # Verify the file was processed despite the error
    assert str(pdf_path) in event_handler.processed_files

def test_monitored_files_list(folder_monitor, temp_dir, mock_callback):
    """Test getting list of monitored files"""
    offers_path = Path(temp_dir) / 'offers'
    invoices_path = Path(temp_dir) / 'invoices'
    offers_path.mkdir()
    invoices_path.mkdir()
    
    # Start monitoring
    folder_monitor.start_monitoring(
        str(offers_path),
        str(invoices_path),
        mock_callback,
        mock_callback
    )
    
    # Create some files
    offer_pdf = create_pdf_file(offers_path, 'offer.pdf')
    invoice_pdf = create_pdf_file(invoices_path, 'invoice.pdf')
    
    # Wait for processing
    time.sleep(2)
    
    # Get monitored files
    monitored_files = folder_monitor.get_monitored_files()
    
    # Verify structure
    assert 'offers' in monitored_files
    assert 'invoices' in monitored_files
    
    # Stop monitoring
    folder_monitor.stop_monitoring()

if __name__ == '__main__':
    pytest.main([__file__])
