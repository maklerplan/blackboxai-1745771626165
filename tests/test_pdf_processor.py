import pytest
from decimal import Decimal
from pathlib import Path
import tempfile
from src.pdf_processor import PDFProcessor, Item, ComparisonResult

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

@pytest.fixture
def sample_items():
    return [
        Item(
            item_code="A123",
            description="Test Item 1",
            quantity=Decimal("10"),
            unit_price=Decimal("15.50"),
            total_price=Decimal("155.00")
        ),
        Item(
            item_code="B456",
            description="Test Item 2",
            quantity=Decimal("5"),
            unit_price=Decimal("25.00"),
            total_price=Decimal("125.00")
        ),
        Item(
            item_code="C789",
            description="Test Item 3",
            quantity=Decimal("2"),
            unit_price=Decimal("50.00"),
            total_price=Decimal("100.00")
        )
    ]

def create_test_pdf(content: str) -> str:
    """Create a temporary PDF file with test content"""
    import fpdf
    
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=content)
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        pdf.output(tmp.name)
        return tmp.name

def test_item_line_total():
    """Test Item class line_total property"""
    item = Item(
        item_code="TEST1",
        description="Test Item",
        quantity=Decimal("2"),
        unit_price=Decimal("10.00"),
        total_price=Decimal("20.00")
    )
    
    assert item.line_total == Decimal("20.00")

def test_extract_items_from_pdf(pdf_processor):
    """Test PDF item extraction"""
    # Create a test PDF with a simple table
    content = """
    Item Code    Description    Quantity    Unit Price    Total
    A123        Test Item 1    10          15.50         155.00
    B456        Test Item 2    5           25.00         125.00
    """
    
    pdf_path = create_test_pdf(content)
    
    try:
        items = pdf_processor.extract_items_from_pdf(pdf_path)
        
        assert len(items) >= 2
        assert any(item.item_code == "A123" for item in items)
        assert any(item.item_code == "B456" for item in items)
        
    finally:
        # Clean up temporary file
        Path(pdf_path).unlink()

def test_compare_documents(pdf_processor, sample_items):
    """Test document comparison"""
    # Create modified items for invoice comparison
    invoice_items = [
        Item(
            item_code="A123",
            description="Test Item 1",
            quantity=Decimal("8"),  # Quantity mismatch
            unit_price=Decimal("15.50"),
            total_price=Decimal("124.00")
        ),
        Item(
            item_code="B456",
            description="Test Item 2",
            quantity=Decimal("5"),
            unit_price=Decimal("26.00"),  # Price mismatch
            total_price=Decimal("130.00")
        ),
        # C789 missing from invoice
        Item(
            item_code="D012",  # Extra item
            description="Test Item 4",
            quantity=Decimal("1"),
            unit_price=Decimal("75.00"),
            total_price=Decimal("75.00")
        )
    ]
    
    results = pdf_processor.compare_documents(sample_items, invoice_items)
    
    # Verify comparison results
    assert len(results) == 4  # 3 original items + 1 extra item
    
    # Check quantity mismatch
    quantity_mismatch = next(r for r in results if r.item_code == "A123")
    assert quantity_mismatch.status == "quantity_mismatch"
    assert quantity_mismatch.quantity_difference == Decimal("2")
    
    # Check price mismatch
    price_mismatch = next(r for r in results if r.item_code == "B456")
    assert price_mismatch.status == "price_mismatch"
    assert price_mismatch.price_difference == Decimal("-1.00")
    
    # Check missing item
    missing_item = next(r for r in results if r.item_code == "C789")
    assert missing_item.status == "missing"
    
    # Check extra item
    extra_item = next(r for r in results if r.item_code == "D012")
    assert extra_item.status == "extra_item"

def test_parse_decimal(pdf_processor):
    """Test decimal parsing with various formats"""
    test_cases = [
        ("1234.56", Decimal("1234.56")),
        ("1,234.56", Decimal("1234.56")),
        ("1.234,56", Decimal("1234.56")),
        ("€1,234.56", Decimal("1234.56")),
        ("$1,234.56", Decimal("1234.56")),
        ("1234,56", Decimal("1234.56")),
        ("invalid", Decimal("0")),
        ("", Decimal("0")),
    ]
    
    for input_str, expected in test_cases:
        assert pdf_processor._parse_decimal(input_str) == expected

def test_process_table(pdf_processor):
    """Test table processing"""
    table = [
        ["Item Code", "Description", "Qty", "Unit Price", "Total"],
        ["A123", "Test Item 1", "10", "15.50", "155.00"],
        ["B456", "Test Item 2", "5", "25.00", "125.00"]
    ]
    
    items = pdf_processor._process_table(table)
    
    assert len(items) == 2
    assert items[0].item_code == "A123"
    assert items[0].quantity == Decimal("10")
    assert items[1].item_code == "B456"
    assert items[1].unit_price == Decimal("25.00")

def test_identify_columns(pdf_processor):
    """Test column identification in table headers"""
    headers = ["Item Number", "Product Description", "Quantity", "Price/Unit", "Line Total"]
    
    columns = pdf_processor._identify_columns(headers)
    
    assert "item_code" in columns
    assert "description" in columns
    assert "quantity" in columns
    assert "unit_price" in columns
    assert "total_price" in columns

def test_process_text(pdf_processor):
    """Test text processing for item extraction"""
    text = """
    Item: A123
    Description: Test Item 1
    Quantity: 10 Units
    Price: €15.50
    
    Item: B456
    Description: Test Item 2
    Quantity: 5 Units
    Price: €25.00
    """
    
    items = pdf_processor._process_text(text)
    
    assert len(items) > 0
    found_items = {item.item_code for item in items}
    assert "A123" in found_items or "B456" in found_items

if __name__ == '__main__':
    pytest.main([__file__])
