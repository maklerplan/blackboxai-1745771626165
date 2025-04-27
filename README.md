# PDF Comparison Tool

A desktop application for comparing offer PDFs with delivery/invoice PDFs to detect discrepancies in quantities, prices, and items.

## Features

- **PDF Document Processing**
  - Extract text and tables from PDFs
  - Intelligent parsing of item details (codes, quantities, prices)
  - Support for various PDF formats and layouts

- **Automated Comparison**
  - Match items between offers and invoices
  - Detect quantity mismatches
  - Identify price discrepancies
  - Track missing or extra items
  - Handle partial deliveries

- **File Monitoring**
  - Watch folders for new PDFs
  - Automatic processing of new documents
  - Support for multiple invoices per offer
  - Integration with network drives (FronDrive/T-Drive)

- **Real-time Notifications**
  - Slack integration for instant alerts
  - Customizable notification triggers
  - Detailed discrepancy reports
  - Support for different notification thresholds

- **User Interface**
  - Modern, intuitive desktop interface
  - Drag-and-drop file handling
  - Real-time comparison results
  - Historical comparison viewer
  - Configurable settings

- **Data Management**
  - Store comparison history
  - Track notification status
  - Generate statistics and reports
  - Automatic cleanup of old records

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-comparison-tool.git
cd pdf-comparison-tool
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example configuration:
```bash
cp config/settings.yaml.example config/settings.yaml
```

2. Edit `config/settings.yaml` to set up:
- Folder paths for offers and invoices
- Slack webhook URL and channel
- Notification preferences
- Processing settings
- Database configuration

## Usage

1. Start the application:
```bash
python src/main.py
```

2. Configure folder monitoring:
   - Set paths for offer and invoice folders
   - Enable automatic monitoring if desired
   - Configure check interval

3. Configure notifications:
   - Enter Slack webhook URL
   - Set notification channel
   - Choose notification triggers
   - Set thresholds for alerts

4. Process documents:
   - Drag and drop PDFs into the application
   - Or let the automatic monitoring handle new files
   - View results in real-time
   - Check Slack for notifications

## Development

### Project Structure
```
pdf-comparison-tool/
├── src/
│   ├── main.py              # Main application entry point
│   ├── pdf_processor.py     # PDF processing and comparison logic
│   ├── file_monitor.py      # File system monitoring
│   ├── notifier.py          # Slack notification system
│   ├── database.py          # Database operations
│   └── config_manager.py    # Configuration management
├── tests/
│   ├── test_pdf_processor.py
│   ├── test_file_monitor.py
│   ├── test_notifier.py
│   ├── test_database.py
│   └── test_config_manager.py
├── config/
│   └── settings.yaml        # Application configuration
└── requirements.txt         # Python dependencies
```

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_pdf_processor.py
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Look for existing issues
3. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Relevant logs

## Acknowledgments

- PyQt6 for the GUI framework
- pdfplumber for PDF text extraction
- watchdog for file system monitoring
- SQLAlchemy for database operations
- pytest for testing framework
