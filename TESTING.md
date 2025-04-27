# How to Test the PDF Comparison Tool

## Quick Start Test

1. First, set up the project:
```bash
# On Unix/Linux/Mac:
./setup.sh

# On Windows:
setup.bat
```

2. Generate test PDFs:
```bash
python tools/generate_test_pdfs.py
```
This will create various test PDFs in the `test_pdfs` directory with different scenarios.

3. Run the example case:
```bash
python examples/case1_perfect_match/run_example.py
```

## Test Different Scenarios

### 1. Perfect Match Test
```bash
# Navigate to test_pdfs directory
cd test_pdfs

# Compare offer with invoice
python ../src/main.py --offer offer_perfect.pdf --invoice invoice_perfect.pdf
```
Expected: All items should match perfectly

### 2. Quantity Mismatch Test
```bash
python ../src/main.py --offer offer_quantity_mismatch.pdf --invoice invoice_quantity_mismatch.pdf
```
Expected: Should show differences in quantities

### 3. Price Mismatch Test
```bash
python ../src/main.py --offer offer_price_mismatch.pdf --invoice invoice_price_mismatch.pdf
```
Expected: Should show differences in prices

### 4. Missing Items Test
```bash
python ../src/main.py --offer offer_missing_items.pdf --invoice invoice_missing_items.pdf
```
Expected: Should show items present in offer but missing in invoice

### 5. Extra Items Test
```bash
python ../src/main.py --offer offer_extra_items.pdf --invoice invoice_extra_items.pdf
```
Expected: Should show extra items in invoice not present in offer

### 6. Partial Delivery Test
```bash
python ../src/main.py --offer offer_partial.pdf --invoice invoice_partial_1.pdf invoice_partial_2.pdf
```
Expected: Should show how partial deliveries add up to complete the order

## Testing with Real PDFs

1. Place your offer PDF in a directory:
```bash
cp your_offer.pdf test_pdfs/
```

2. Place your invoice PDF(s) in the same directory:
```bash
cp your_invoice.pdf test_pdfs/
```

3. Run the comparison:
```bash
python src/main.py --offer test_pdfs/your_offer.pdf --invoice test_pdfs/your_invoice.pdf
```

## Testing Automatic Monitoring

1. Configure monitoring folders in config/settings.yaml:
```yaml
monitoring:
  enabled: true
  check_interval: 5  # minutes
  folders:
    offers: "/path/to/offers/folder"
    invoices: "/path/to/invoices/folder"
```

2. Start the application in monitoring mode:
```bash
python src/main.py --monitor
```

3. Drop PDFs into the configured folders:
- Place offer PDFs in the offers folder
- Place invoice PDFs in the invoices folder
- The tool will automatically detect and compare them

## Testing Slack Notifications

1. Configure Slack in config/settings.yaml:
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "your-webhook-url"
    channel: "#your-channel"
```

2. Run a comparison:
```bash
python src/main.py --offer test_pdfs/offer_price_mismatch.pdf --invoice test_pdfs/invoice_price_mismatch.pdf
```

3. Check your Slack channel for notifications

## Testing via GUI

1. Start the GUI application:
```bash
python src/main.py
```

2. Use the interface to:
- Drop PDFs into the offer and invoice zones
- Click "Compare" to run the comparison
- View results in the comparison panel
- Check history in the history tab

## Running Unit Tests

1. Run all tests:
```bash
python run_tests.py
```

2. Run specific test file:
```bash
python run_tests.py --file tests/test_pdf_processor.py
```

3. Run with coverage:
```bash
python run_tests.py --coverage --html
```

## Common Test Cases to Try

1. **Format Variations**:
- Test with different PDF layouts
- Test with different number formats (1.000,00 vs 1,000.00)
- Test with different currency symbols (€, $, £)

2. **Edge Cases**:
- Empty PDFs
- PDFs with missing data
- Very large PDFs
- Scanned PDFs (OCR test)

3. **Error Cases**:
- Invalid PDF files
- Missing files
- Permission issues
- Network issues (for Slack notifications)

## Troubleshooting Tests

If you encounter issues:

1. Check the logs:
```bash
cat logs/comparison_tool.log
```

2. Run setup verification:
```bash
python test_setup.py
```

3. Clean and reset:
```bash
python dev.py clean --all
python dev.py setup
```

4. Generate fresh test data:
```bash
python tools/generate_test_pdfs.py
```

For more help, check the main README.md or create an issue on the project repository.
