#!/usr/bin/env python3
"""
Example script demonstrating how to use the PDF Comparison Tool
with a perfect match case.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.pdf_processor import PDFProcessor
from src.notifier import SlackNotifier, NotificationConfig
from src.database import DatabaseManager

def main():
    """Run the example comparison"""
    print("PDF Comparison Tool - Perfect Match Example")
    print("=========================================")
    
    # Initialize components
    pdf_processor = PDFProcessor()
    
    # Get file paths
    current_dir = Path(__file__).parent
    offer_path = current_dir / "offer.pdf"
    invoice_path = current_dir / "invoice.pdf"
    
    print(f"\nProcessing files:")
    print(f"Offer:   {offer_path}")
    print(f"Invoice: {invoice_path}")
    
    # Extract items from PDFs
    print("\nExtracting items from offer...")
    offer_items = pdf_processor.extract_items_from_pdf(str(offer_path))
    print(f"Found {len(offer_items)} items in offer")
    
    print("\nExtracting items from invoice...")
    invoice_items = pdf_processor.extract_items_from_pdf(str(invoice_path))
    print(f"Found {len(invoice_items)} items in invoice")
    
    # Compare documents
    print("\nComparing documents...")
    results = pdf_processor.compare_documents(offer_items, invoice_items)
    
    # Print results
    print("\nComparison Results:")
    print("-----------------")
    
    for result in results:
        print(f"\nItem: {result.item_code} - {result.description}")
        print(f"Status: {result.status}")
        print(f"Quantities: Offer={result.offer_quantity}, Invoice={result.delivered_quantity}")
        print(f"Prices: Offer=€{result.offer_price}, Invoice=€{result.invoiced_price}")
        if result.quantity_difference != 0:
            print(f"Quantity difference: {result.quantity_difference}")
        if result.price_difference != 0:
            print(f"Price difference: €{result.price_difference}")
    
    # Store results in database
    print("\nStoring results in database...")
    db_manager = DatabaseManager("data/comparison_history.db")
    
    summary = {
        'total_items': len(results),
        'matches': len([r for r in results if r.status == 'match']),
        'quantity_mismatches': len([r for r in results if r.status == 'quantity_mismatch']),
        'price_mismatches': len([r for r in results if r.status == 'price_mismatch']),
        'missing_items': len([r for r in results if r.status == 'missing']),
        'extra_items': len([r for r in results if r.status == 'extra_item']),
        'total_quantity_difference': sum(abs(r.quantity_difference) for r in results),
        'total_price_difference': sum(abs(r.price_difference) for r in results)
    }
    
    record_id = db_manager.store_comparison(
        offer_path=str(offer_path),
        invoice_paths=[str(invoice_path)],
        status='success',
        summary=summary,
        results=[{
            'item_code': r.item_code,
            'description': r.description,
            'status': r.status,
            'offer_quantity': float(r.offer_quantity),
            'delivered_quantity': float(r.delivered_quantity),
            'offer_price': float(r.offer_price),
            'invoiced_price': float(r.invoiced_price),
            'quantity_difference': float(r.quantity_difference),
            'price_difference': float(r.price_difference)
        } for r in results]
    )
    
    print(f"Results stored with ID: {record_id}")
    
    # Send notification (if configured)
    if os.environ.get('SLACK_WEBHOOK_URL'):
        print("\nSending Slack notification...")
        notifier = SlackNotifier(NotificationConfig(
            webhook_url=os.environ['SLACK_WEBHOOK_URL'],
            channel="#pdf-comparison-alerts",
            notify_price_discrepancies=True,
            notify_quantity_mismatches=True,
            notify_missing_items=True,
            notify_successful_comparisons=True,
            price_threshold=0,
            quantity_threshold=0
        ))
        
        notifier.send_comparison_results(
            offer_path=str(offer_path),
            invoice_paths=[str(invoice_path)],
            results=[vars(r) for r in results],
            summary=summary
        )
    
    print("\nExample completed successfully!")
    print("\nNote: This example demonstrates a perfect match case where all items,")
    print("quantities, and prices match exactly between the offer and invoice.")
    print("\nTry modifying the PDF files to test different scenarios like:")
    print("- Quantity mismatches")
    print("- Price discrepancies")
    print("- Missing items")
    print("- Extra items")

if __name__ == "__main__":
    main()
