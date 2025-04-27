import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QCheckBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path

class PDFComparisonTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Comparison Tool")
        self.setMinimumSize(1024, 768)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("PDF Comparison Tool")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        settings_btn = QPushButton("Settings")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(settings_btn)
        layout.addLayout(header)
        
        # Content area
        content = QHBoxLayout()
        
        # Left panel - Document Management
        left_panel = self._create_document_panel()
        content.addWidget(left_panel)
        
        # Right panel - Results
        right_panel = self._create_results_panel()
        content.addWidget(right_panel)
        
        layout.addLayout(content)
        
        # Footer
        footer = self._create_footer()
        layout.addLayout(footer)
        
        # Connect signals
        settings_btn.clicked.connect(self.show_settings)
    
    def _create_document_panel(self):
        panel = QWidget()
        panel.setProperty("class", "panel")
        layout = QVBoxLayout(panel)
        
        # Offer section
        layout.addWidget(QLabel("Offer Document"))
        offer_drop = DropArea("Drop Offer PDF here")
        layout.addWidget(offer_drop)
        
        # Invoice section
        layout.addWidget(QLabel("Invoice Documents"))
        invoice_drop = DropArea("Drop Invoice PDFs here")
        layout.addWidget(invoice_drop)
        
        return panel
    
    def _create_results_panel(self):
        panel = QWidget()
        panel.setProperty("class", "panel")
        layout = QVBoxLayout(panel)
        
        # Status
        status = QLabel("Ready for comparison")
        status.setStyleSheet("color: green;")
        layout.addWidget(status)
        
        # Summary
        summary = QWidget()
        summary_layout = QHBoxLayout(summary)
        total_items = QLabel("Total Items: -")
        discrepancies = QLabel("Discrepancies: -")
        summary_layout.addWidget(total_items)
        summary_layout.addWidget(discrepancies)
        layout.addWidget(summary)
        
        # Results area
        results = QWidget()
        layout.addWidget(results)
        
        return panel
    
    def _create_footer(self):
        footer = QHBoxLayout()
        
        # Auto-monitor checkbox
        monitor_cb = QCheckBox("Enable automatic monitoring")
        footer.addWidget(monitor_cb)
        
        footer.addStretch()
        
        # Action buttons
        history_btn = QPushButton("View History")
        compare_btn = QPushButton("Start Comparison")
        footer.addWidget(history_btn)
        footer.addWidget(compare_btn)
        
        return footer
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

class DropArea(QWidget):
    def __init__(self, placeholder_text):
        super().__init__()
        layout = QVBoxLayout(self)
        
        label = QLabel(placeholder_text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            DropArea {
                border: 2px dashed #ccc;
                border-radius: 5px;
                padding: 20px;
            }
            DropArea:hover {
                border-color: #999;
            }
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                print(f"Received PDF: {file_path}")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Folder monitoring section
        monitoring_group = QGroupBox("Folder Monitoring")
        monitoring_layout = QVBoxLayout()
        
        # Offer folder
        offer_layout = QHBoxLayout()
        offer_path = QLineEdit()
        offer_browse = QPushButton("Browse")
        offer_layout.addWidget(QLabel("Offers Folder:"))
        offer_layout.addWidget(offer_path)
        offer_layout.addWidget(offer_browse)
        monitoring_layout.addLayout(offer_layout)
        
        # Invoice folder
        invoice_layout = QHBoxLayout()
        invoice_path = QLineEdit()
        invoice_browse = QPushButton("Browse")
        invoice_layout.addWidget(QLabel("Invoices Folder:"))
        invoice_layout.addWidget(invoice_path)
        invoice_layout.addWidget(invoice_browse)
        monitoring_layout.addLayout(invoice_layout)
        
        monitoring_group.setLayout(monitoring_layout)
        layout.addWidget(monitoring_group)
        
        # Slack settings
        slack_group = QGroupBox("Slack Integration")
        slack_layout = QVBoxLayout()
        
        webhook_layout = QHBoxLayout()
        webhook_layout.addWidget(QLabel("Webhook URL:"))
        webhook_layout.addWidget(QLineEdit())
        slack_layout.addLayout(webhook_layout)
        
        channel_layout = QHBoxLayout()
        channel_layout.addWidget(QLabel("Channel:"))
        channel_layout.addWidget(QLineEdit())
        slack_layout.addLayout(channel_layout)
        
        slack_group.setLayout(slack_layout)
        layout.addWidget(slack_group)
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("Save")
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)
        
        # Connect signals
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.accept)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background: #f0f0f0;
        }
        .panel {
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
        }
        QPushButton {
            padding: 5px 15px;
            border-radius: 3px;
            background: #007bff;
            color: white;
        }
        QPushButton:hover {
            background: #0056b3;
        }
    """)
    
    window = PDFComparisonTool()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
