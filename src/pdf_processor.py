import pdfplumber
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
import re

@dataclass
class Item:
    """Represents an item from either an offer or invoice"""
    item_code: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal
    
    @property
    def line_total(self) -> Decimal:
        return self.quantity * self.unit_price

@dataclass
class ComparisonResult:
    """Represents the result of comparing an item between offer and invoices"""
    item_code: str
    description: str
    offer_quantity: Decimal
    delivered_quantity: Decimal
    offer_price: Decimal
    invoiced_price: Decimal
    quantity_difference: Decimal
    price_difference: Decimal
    status: str  # 'match', 'quantity_mismatch', 'price_mismatch', 'missing'

class PDFProcessor:
    def __init__(self):
        self.price_tolerance = Decimal('0.02')  # 2% tolerance for price differences
    
    def extract_items_from_pdf(self, pdf_path: str) -> List[Item]:
        """Extract items from a PDF document"""
        items = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    # Extract tables from the page
                    tables = page.extract_tables()
                    
                    for table in tables:
                        items.extend(self._process_table(table))
                        
                    # Also look for text that might contain item information
                    text = page.extract_text()
                    items.extend(self._process_text(text))
                    
        except Exception as e:
            print(f"Error processing PDF {pdf_path}: {str(e)}")
            return []
            
        return items
    
    def _process_table(self, table: List[List[str]]) -> List[Item]:
        """Process a table extracted from PDF and convert to Items"""
        items = []
        
        if not table:
            return items
            
        # Try to identify column positions based on headers
        header_row = table[0]
        column_indices = self._identify_columns(header_row)
        
        if not column_indices:
            return items
            
        # Process each row
        for row in table[1:]:
            try:
                item = self._parse_row(row, column_indices)
                if item:
                    items.append(item)
            except Exception as e:
                print(f"Error processing row {row}: {str(e)}")
                continue
                
        return items
    
    def _identify_columns(self, header_row: List[str]) -> Dict[str, int]:
        """Identify the position of important columns in the table"""
        columns = {}
        
        for i, header in enumerate(header_row):
            header_lower = str(header).lower()
            
            if any(x in header_lower for x in ['item', 'code', 'article']):
                columns['item_code'] = i
            elif any(x in header_lower for x in ['desc', 'description', 'product']):
                columns['description'] = i
            elif any(x in header_lower for x in ['qty', 'quantity', 'amount']):
                columns['quantity'] = i
            elif any(x in header_lower for x in ['price', 'unit']):
                columns['unit_price'] = i
            elif any(x in header_lower for x in ['total', 'sum']):
                columns['total_price'] = i
                
        return columns
    
    def _parse_row(self, row: List[str], column_indices: Dict[str, int]) -> Optional[Item]:
        """Parse a row from the table into an Item object"""
        try:
            # Extract values using column indices
            item_code = str(row[column_indices.get('item_code', 0)]).strip()
            description = str(row[column_indices.get('description', 1)]).strip()
            
            # Parse quantity and prices, handling various formats
            quantity = self._parse_decimal(row[column_indices.get('quantity', 2)])
            unit_price = self._parse_decimal(row[column_indices.get('unit_price', 3)])
            total_price = self._parse_decimal(row[column_indices.get('total_price', 4)])
            
            if item_code and quantity and unit_price:
                return Item(
                    item_code=item_code,
                    description=description,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price or (quantity * unit_price)
                )
                
        except Exception as e:
            print(f"Error parsing row: {str(e)}")
            return None
            
        return None
    
    def _process_text(self, text: str) -> List[Item]:
        """Extract items from text using regex patterns"""
        items = []
        
        # Common patterns for item information in text
        patterns = [
            # Pattern 1: Item code followed by quantity and price
            r'(?P<item_code>[A-Z0-9-]+)\s+'
            r'(?P<description>[^0-9\n]+)\s+'
            r'(?P<quantity>\d+(?:\.\d+)?)\s+'
            r'(?P<unit_price>\d+(?:\.\d+)?)',
            
            # Add more patterns as needed for different document formats
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    item = Item(
                        item_code=match.group('item_code'),
                        description=match.group('description').strip(),
                        quantity=Decimal(match.group('quantity')),
                        unit_price=Decimal(match.group('unit_price')),
                        total_price=Decimal(match.group('quantity')) * Decimal(match.group('unit_price'))
                    )
                    items.append(item)
                except Exception as e:
                    print(f"Error parsing text match: {str(e)}")
                    continue
                    
        return items
    
    def _parse_decimal(self, value: str) -> Decimal:
        """Parse a string into a Decimal, handling various number formats"""
        if not value:
            return Decimal('0')
            
        # Remove currency symbols and other non-numeric characters
        clean_value = re.sub(r'[^\d.,\-]', '', str(value))
        
        # Handle different decimal separators
        if ',' in clean_value and '.' in clean_value:
            # Format: 1,234.56
            clean_value = clean_value.replace(',', '')
        elif ',' in clean_value:
            # Format: 1234,56
            clean_value = clean_value.replace(',', '.')
            
        try:
            return Decimal(clean_value)
        except:
            return Decimal('0')
    
    def compare_documents(self, offer_items: List[Item], invoice_items: List[Item]) -> List[ComparisonResult]:
        """Compare items from offer with items from invoices"""
        results = []
        
        # Group invoice items by item code
        invoice_items_dict = {}
        for item in invoice_items:
            if item.item_code in invoice_items_dict:
                # Sum quantities for the same item
                existing = invoice_items_dict[item.item_code]
                existing.quantity += item.quantity
                existing.total_price += item.total_price
            else:
                invoice_items_dict[item.item_code] = item
        
        # Compare each offer item with invoice items
        for offer_item in offer_items:
            invoice_item = invoice_items_dict.get(offer_item.item_code)
            
            if not invoice_item:
                # Item in offer but not in invoices
                results.append(ComparisonResult(
                    item_code=offer_item.item_code,
                    description=offer_item.description,
                    offer_quantity=offer_item.quantity,
                    delivered_quantity=Decimal('0'),
                    offer_price=offer_item.unit_price,
                    invoiced_price=Decimal('0'),
                    quantity_difference=offer_item.quantity,
                    price_difference=Decimal('0'),
                    status='missing'
                ))
                continue
            
            # Calculate differences
            quantity_diff = offer_item.quantity - invoice_item.quantity
            price_diff = offer_item.unit_price - invoice_item.unit_price
            
            # Determine status
            status = 'match'
            if quantity_diff != 0:
                status = 'quantity_mismatch'
            elif abs(price_diff / offer_item.unit_price) > self.price_tolerance:
                status = 'price_mismatch'
            
            results.append(ComparisonResult(
                item_code=offer_item.item_code,
                description=offer_item.description,
                offer_quantity=offer_item.quantity,
                delivered_quantity=invoice_item.quantity,
                offer_price=offer_item.unit_price,
                invoiced_price=invoice_item.unit_price,
                quantity_difference=quantity_diff,
                price_difference=price_diff,
                status=status
            ))
        
        # Check for items in invoices but not in offer
        offer_item_codes = {item.item_code for item in offer_items}
        for invoice_item in invoice_items_dict.values():
            if invoice_item.item_code not in offer_item_codes:
                results.append(ComparisonResult(
                    item_code=invoice_item.item_code,
                    description=invoice_item.description,
                    offer_quantity=Decimal('0'),
                    delivered_quantity=invoice_item.quantity,
                    offer_price=Decimal('0'),
                    invoiced_price=invoice_item.unit_price,
                    quantity_difference=-invoice_item.quantity,
                    price_difference=-invoice_item.unit_price,
                    status='extra_item'
                ))
        
        return results

    def generate_summary(self, results: List[ComparisonResult]) -> Dict:
        """Generate a summary of comparison results"""
        summary = {
            'total_items': len(results),
            'matches': 0,
            'quantity_mismatches': 0,
            'price_mismatches': 0,
            'missing_items': 0,
            'extra_items': 0,
            'total_quantity_difference': Decimal('0'),
            'total_price_difference': Decimal('0')
        }
        
        for result in results:
            if result.status == 'match':
                summary['matches'] += 1
            elif result.status == 'quantity_mismatch':
                summary['quantity_mismatches'] += 1
            elif result.status == 'price_mismatch':
                summary['price_mismatches'] += 1
            elif result.status == 'missing':
                summary['missing_items'] += 1
            elif result.status == 'extra_item':
                summary['extra_items'] += 1
                
            summary['total_quantity_difference'] += abs(result.quantity_difference)
            summary['total_price_difference'] += abs(result.price_difference)
        
        return summary
