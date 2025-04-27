#!/usr/bin/env python3
"""
Generate sample PDFs for testing the PDF Comparison Tool.
Creates offer and invoice PDFs with various test cases.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
import random
from decimal import Decimal
import fpdf

class PDFGenerator:
    def __init__(self):
        self.items = [
            {
                'code': 'A123',
                'description': 'Premium Widget',
                'unit_price': Decimal('15.50')
            },
            {
                'code': 'B456',
                'description': 'Deluxe Gadget',
                'unit_price': Decimal('25.00')
            },
            {
                'code': 'C789',
                'description': 'Super Tool',
                'unit_price': Decimal('50.00')
            },
            {
                'code': 'D012',
                'description': 'Mega Device',
                'unit_price': Decimal('75.00')
            }
        ]

    def create_pdf(self, filename: str, title: str, items: list, date: datetime):
        """Create a PDF document with the specified items"""
        pdf = fpdf.FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, ln=True, align='C')
        
        # Date and document number
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Date: {date.strftime('%Y-%m-%d')}", ln=True)
        pdf.cell(0, 10, f"Document #: {random.randint(10000, 99999)}", ln=True)
        
        # Table header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(30, 10, "Item Code", border=1)
        pdf.cell(60, 10, "Description", border=1)
        pdf.cell(30, 10, "Quantity", border=1)
        pdf.cell(35, 10, "Unit Price", border=1)
        pdf.cell(35, 10, "Total", border=1, ln=True)
        
        # Table content
        pdf.set_font("Arial", size=12)
        total = Decimal('0')
        
        for item in items:
            quantity = item['quantity']
            unit_price = item['unit_price']
            line_total = quantity * unit_price
            total += line_total
            
            pdf.cell(30, 10, item['code'], border=1)
            pdf.cell(60, 10, item['description'], border=1)
            pdf.cell(30, 10, str(quantity), border=1)
            pdf.cell(35, 10, f"€{unit_price:.2f}", border=1)
            pdf.cell(35, 10, f"€{line_total:.2f}", border=1, ln=True)
        
        # Total
        pdf.cell(155, 10, "Total:", border=1)
        pdf.cell(35, 10, f"€{total:.2f}", border=1, ln=True)
        
        # Save PDF
        pdf.output(filename)

    def generate_test_cases(self, output_dir: str = "test_pdfs"):
        """Generate various test cases"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        base_date = datetime.now()
        
        # Test Case 1: Perfect match
        items = []
        for item in self.items[:3]:
            items.append({
                **item,
                'quantity': 5
            })
        
        self.create_pdf(
            f"{output_dir}/offer_perfect.pdf",
            "Offer - Perfect Match",
            items,
            base_date
        )
        
        self.create_pdf(
            f"{output_dir}/invoice_perfect.pdf",
            "Invoice - Perfect Match",
            items,
            base_date + timedelta(days=1)
        )
        
        # Test Case 2: Quantity mismatch
        invoice_items = []
        for item in items:
            invoice_items.append({
                **item,
                'quantity': item['quantity'] - random.randint(1, 2)
            })
        
        self.create_pdf(
            f"{output_dir}/offer_quantity_mismatch.pdf",
            "Offer - Quantity Mismatch",
            items,
            base_date
        )
        
        self.create_pdf(
            f"{output_dir}/invoice_quantity_mismatch.pdf",
            "Invoice - Quantity Mismatch",
            invoice_items,
            base_date + timedelta(days=1)
        )
        
        # Test Case 3: Price mismatch
        invoice_items = []
        for item in items:
            invoice_items.append({
                **item,
                'unit_price': item['unit_price'] * Decimal('1.1')  # 10% price increase
            })
        
        self.create_pdf(
            f"{output_dir}/offer_price_mismatch.pdf",
            "Offer - Price Mismatch",
            items,
            base_date
        )
        
        self.create_pdf(
            f"{output_dir}/invoice_price_mismatch.pdf",
            "Invoice - Price Mismatch",
            invoice_items,
            base_date + timedelta(days=1)
        )
        
        # Test Case 4: Missing items
        self.create_pdf(
            f"{output_dir}/offer_missing_items.pdf",
            "Offer - Missing Items",
            items,
            base_date
        )
        
        self.create_pdf(
            f"{output_dir}/invoice_missing_items.pdf",
            "Invoice - Missing Items",
            items[:-1],  # Remove last item
            base_date + timedelta(days=1)
        )
        
        # Test Case 5: Extra items
        invoice_items = items.copy()
        invoice_items.append({
            **self.items[3],  # Add extra item
            'quantity': 3
        })
        
        self.create_pdf(
            f"{output_dir}/offer_extra_items.pdf",
            "Offer - Extra Items",
            items,
            base_date
        )
        
        self.create_pdf(
            f"{output_dir}/invoice_extra_items.pdf",
            "Invoice - Extra Items",
            invoice_items,
            base_date + timedelta(days=1)
        )
        
        # Test Case 6: Multiple invoices (partial deliveries)
        self.create_pdf(
            f"{output_dir}/offer_partial.pdf",
            "Offer - Partial Delivery",
            items,
            base_date
        )
        
        # First partial delivery
        invoice_items1 = []
        for item in items:
            invoice_items1.append({
                **item,
                'quantity': item['quantity'] // 2
            })
        
        self.create_pdf(
            f"{output_dir}/invoice_partial_1.pdf",
            "Invoice - Partial Delivery 1",
            invoice_items1,
            base_date + timedelta(days=1)
        )
        
        # Second partial delivery
        invoice_items2 = []
        for item in items:
            remaining = item['quantity'] - (item['quantity'] // 2)
            invoice_items2.append({
                **item,
                'quantity': remaining
            })
        
        self.create_pdf(
            f"{output_dir}/invoice_partial_2.pdf",
            "Invoice - Partial Delivery 2",
            invoice_items2,
            base_date + timedelta(days=2)
        )

def main():
    """Generate test PDFs"""
    print("Generating test PDFs...")
    generator = PDFGenerator()
    generator.generate_test_cases()
    print("Test PDFs generated in the 'test_pdfs' directory")
    
    # List generated files
    print("\nGenerated files:")
    for file in sorted(Path("test_pdfs").glob("*.pdf")):
        print(f"- {file.name}")

if __name__ == "__main__":
    main()
