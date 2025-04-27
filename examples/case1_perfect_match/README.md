# Perfect Match Example

This example demonstrates the basic usage of the PDF Comparison Tool with a simple case where the offer and invoice match perfectly.

## Files

- `offer.pdf`: Sample offer document containing 3 items
- `invoice.pdf`: Sample invoice document with matching items
- `run_example.py`: Script demonstrating how to use the comparison tool

## Item Details

The documents contain these items:
1. Widget (A123)
   - Quantity: 10
   - Price: €15.50
   - Total: €155.00

2. Gadget (B456)
   - Quantity: 5
   - Price: €25.00
   - Total: €125.00

3. Tool (C789)
   - Quantity: 2
   - Price: €50.00
   - Total: €100.00

Total Amount: €380.00

## Running the Example

1. Ensure you've installed the PDF Comparison Tool:
   ```bash
   # From project root
   ./setup.sh  # or setup.bat on Windows
   ```

2. Run the example:
   ```bash
   # From project root
   python examples/case1_perfect_match/run_example.py
   ```

3. Optional: Set up Slack notifications
   ```bash
   export SLACK_WEBHOOK_URL="your-webhook-url"
   ```

## Expected Output

The script will:
1. Extract items from both PDFs
2. Compare the documents
3. Print the comparison results
4. Store the results in the database
5. Send a Slack notification (if configured)

Since this is a perfect match case, you should see:
- All items match exactly
- No quantity mismatches
- No price discrepancies
- No missing or extra items

## Modifying the Example

You can modify the PDF files to test different scenarios:

1. Quantity Mismatch:
   - Change quantities in `invoice.pdf`
   - Example: Change Widget quantity from 10 to 8

2. Price Discrepancy:
   - Modify prices in `invoice.pdf`
   - Example: Change Gadget price from €25.00 to €27.50

3. Missing Items:
   - Remove an item from `invoice.pdf`
   - Example: Remove the last item (Tool)

4. Extra Items:
   - Add a new item to `invoice.pdf`
   - Example: Add "Extra Item (D012), Quantity: 1, Price: €75.00"

## Understanding the Code

The example demonstrates:
1. Initializing the PDF processor
2. Loading and extracting data from PDFs
3. Comparing documents
4. Handling comparison results
5. Storing results in the database
6. Sending notifications

Key components used:
- `PDFProcessor`: Handles PDF parsing and comparison
- `DatabaseManager`: Stores comparison history
- `SlackNotifier`: Sends notifications

## Next Steps

After understanding this basic example, you can:
1. Try other example cases (quantity mismatches, price discrepancies, etc.)
2. Integrate the comparison logic into your own code
3. Customize the notification format
4. Add more complex comparison rules

## Troubleshooting

1. PDF Extraction Issues:
   - Ensure PDFs are text-based (not scanned images)
   - Check PDF formatting matches expected structure

2. Database Errors:
   - Verify database path exists
   - Check write permissions

3. Notification Issues:
   - Verify Slack webhook URL is correct
   - Check network connectivity

For more help, check the main project documentation or create an issue on GitHub.
