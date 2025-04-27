import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Dict, Set
import logging
from datetime import datetime, timedelta
from queue import Queue
import threading

class PDFEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], None], file_type: str):
        """
        Initialize the event handler
        
        Args:
            callback: Function to call when a PDF is detected
            file_type: Type of files to monitor ('offer' or 'invoice')
        """
        self.callback = callback
        self.file_type = file_type
        self.processed_files: Set[str] = set()
        self.processing_queue = Queue()
        self.start_processing_thread()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith('.pdf'):
            self._handle_pdf(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.lower().endswith('.pdf'):
            self._handle_pdf(event.src_path)

    def _handle_pdf(self, file_path: str):
        """Queue the PDF for processing if it hasn't been processed recently"""
        if file_path not in self.processed_files:
            self.processing_queue.put(file_path)
            self.processed_files.add(file_path)

    def start_processing_thread(self):
        """Start a thread to process PDFs from the queue"""
        def process_queue():
            while True:
                try:
                    # Get file path from queue with timeout
                    file_path = self.processing_queue.get(timeout=1)
                    
                    # Wait briefly to ensure file is completely written
                    time.sleep(1)
                    
                    # Process the file
                    try:
                        self.callback(file_path)
                        logging.info(f"Processed {self.file_type} PDF: {file_path}")
                    except Exception as e:
                        logging.error(f"Error processing {file_path}: {str(e)}")
                    
                    # Remove from processed files after some time
                    threading.Timer(
                        300,  # 5 minutes
                        lambda f: self.processed_files.discard(f),
                        args=[file_path]
                    ).start()
                    
                except Queue.Empty:
                    continue
                except Exception as e:
                    logging.error(f"Error in processing thread: {str(e)}")
                    time.sleep(1)

        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()

class FolderMonitor:
    def __init__(self):
        self.observer = Observer()
        self.handlers: Dict[str, PDFEventHandler] = {}
        self.monitoring = False
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def start_monitoring(self, 
                        offers_path: str, 
                        invoices_path: str,
                        offer_callback: Callable[[str], None],
                        invoice_callback: Callable[[str], None]):
        """
        Start monitoring folders for PDF changes
        
        Args:
            offers_path: Path to folder containing offer PDFs
            invoices_path: Path to folder containing invoice PDFs
            offer_callback: Function to call when new offer PDF is detected
            invoice_callback: Function to call when new invoice PDF is detected
        """
        try:
            # Create handlers for offers and invoices
            offer_handler = PDFEventHandler(offer_callback, 'offer')
            invoice_handler = PDFEventHandler(invoice_callback, 'invoice')
            
            # Store handlers
            self.handlers['offer'] = offer_handler
            self.handlers['invoice'] = invoice_handler
            
            # Schedule monitoring for both paths
            self.observer.schedule(offer_handler, offers_path, recursive=False)
            self.observer.schedule(invoice_handler, invoices_path, recursive=False)
            
            # Start the observer
            self.observer.start()
            self.monitoring = True
            
            logging.info(f"Started monitoring folders:")
            logging.info(f"Offers: {offers_path}")
            logging.info(f"Invoices: {invoices_path}")
            
        except Exception as e:
            logging.error(f"Error starting folder monitoring: {str(e)}")
            self.stop_monitoring()
            raise

    def stop_monitoring(self):
        """Stop monitoring folders"""
        try:
            if self.monitoring:
                self.observer.stop()
                self.observer.join()
                self.monitoring = False
                logging.info("Stopped folder monitoring")
        except Exception as e:
            logging.error(f"Error stopping folder monitoring: {str(e)}")

    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self.monitoring

    def get_monitored_files(self) -> Dict[str, Set[str]]:
        """Get list of currently monitored files"""
        return {
            'offers': self.handlers['offer'].processed_files.copy(),
            'invoices': self.handlers['invoice'].processed_files.copy()
        }

class AutoProcessor:
    def __init__(self, 
                 monitor: FolderMonitor,
                 comparison_callback: Callable[[str, list[str]], None]):
        """
        Initialize the auto processor
        
        Args:
            monitor: FolderMonitor instance
            comparison_callback: Function to call with offer and invoice paths
        """
        self.monitor = monitor
        self.comparison_callback = comparison_callback
        self.pending_offers: Dict[str, datetime] = {}
        self.processing_lock = threading.Lock()
        
        # Start the processing thread
        self.start_processing_thread()

    def handle_offer(self, offer_path: str):
        """Handle new offer PDF"""
        with self.processing_lock:
            self.pending_offers[offer_path] = datetime.now()

    def handle_invoice(self, invoice_path: str):
        """Handle new invoice PDF"""
        with self.processing_lock:
            # Get all pending offers
            current_offers = self.pending_offers.copy()
            
            # Process each pending offer with this invoice
            for offer_path, timestamp in current_offers.items():
                try:
                    self.comparison_callback(offer_path, [invoice_path])
                    logging.info(f"Compared offer {offer_path} with invoice {invoice_path}")
                except Exception as e:
                    logging.error(f"Error comparing {offer_path} with {invoice_path}: {str(e)}")

    def start_processing_thread(self):
        """Start thread to clean up old pending offers"""
        def cleanup_pending():
            while True:
                try:
                    with self.processing_lock:
                        current_time = datetime.now()
                        # Remove offers older than 24 hours
                        expired = [
                            path for path, timestamp in self.pending_offers.items()
                            if current_time - timestamp > timedelta(hours=24)
                        ]
                        for path in expired:
                            del self.pending_offers[path]
                            logging.info(f"Removed expired offer: {path}")
                    
                    # Sleep for 1 hour before next cleanup
                    time.sleep(3600)
                    
                except Exception as e:
                    logging.error(f"Error in cleanup thread: {str(e)}")
                    time.sleep(60)

        thread = threading.Thread(target=cleanup_pending, daemon=True)
        thread.start()
