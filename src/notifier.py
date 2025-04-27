from typing import Dict, List, Optional
import json
import requests
import logging
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass
class NotificationConfig:
    """Configuration for notifications"""
    webhook_url: str
    channel: str
    notify_price_discrepancies: bool = True
    notify_quantity_mismatches: bool = True
    notify_missing_items: bool = True
    notify_successful_comparisons: bool = False
    price_threshold: Decimal = Decimal('0.0')  # Minimum price difference to trigger notification
    quantity_threshold: int = 0  # Minimum quantity difference to trigger notification

class SlackNotifier:
    def __init__(self, config: NotificationConfig):
        """
        Initialize the Slack notifier
        
        Args:
            config: NotificationConfig instance with Slack settings
        """
        self.config = config
        self.session = requests.Session()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def send_comparison_results(self, 
                              offer_path: str, 
                              invoice_paths: List[str], 
                              results: List[Dict],
                              summary: Dict) -> bool:
        """
        Send comparison results to Slack
        
        Args:
            offer_path: Path to the offer PDF
            invoice_paths: List of paths to invoice PDFs
            results: List of comparison results
            summary: Summary of comparison results
        
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            # Determine if notification should be sent based on configuration
            should_notify = self._should_send_notification(summary)
            
            if not should_notify:
                logging.info("No notification needed based on current configuration")
                return True

            # Create message blocks
            blocks = self._create_message_blocks(offer_path, invoice_paths, results, summary)
            
            # Send message to Slack
            response = self.session.post(
                self.config.webhook_url,
                json={
                    "channel": self.config.channel,
                    "blocks": blocks
                }
            )
            
            if response.status_code != 200:
                logging.error(f"Error sending Slack notification: {response.text}")
                return False
                
            logging.info("Successfully sent comparison results to Slack")
            return True
            
        except Exception as e:
            logging.error(f"Error sending comparison results to Slack: {str(e)}")
            return False

    def _should_send_notification(self, summary: Dict) -> bool:
        """Determine if a notification should be sent based on the results and configuration"""
        
        # Always notify for missing items if enabled
        if self.config.notify_missing_items and summary['missing_items'] > 0:
            return True
            
        # Check quantity mismatches
        if (self.config.notify_quantity_mismatches and 
            summary['quantity_mismatches'] > 0 and 
            summary['total_quantity_difference'] >= self.config.quantity_threshold):
            return True
            
        # Check price discrepancies
        if (self.config.notify_price_discrepancies and 
            summary['price_mismatches'] > 0 and 
            summary['total_price_difference'] >= self.config.price_threshold):
            return True
            
        # Notify for successful comparisons if enabled
        if (self.config.notify_successful_comparisons and 
            summary['matches'] == summary['total_items']):
            return True
            
        return False

    def _create_message_blocks(self, 
                             offer_path: str, 
                             invoice_paths: List[str], 
                             results: List[Dict],
                             summary: Dict) -> List[Dict]:
        """Create formatted message blocks for Slack"""
        
        blocks = []
        
        # Header section
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 PDF Comparison Results"
            }
        })
        
        # Files section
        files_text = f"*Offer:* {self._format_path(offer_path)}\n"
        files_text += "*Invoices:*\n" + "\n".join(
            f"• {self._format_path(path)}" for path in invoice_paths
        )
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": files_text
            }
        })
        
        # Summary section
        summary_text = self._create_summary_text(summary)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": summary_text
            }
        })
        
        # Add divider
        blocks.append({"type": "divider"})
        
        # Details section for discrepancies
        if summary['quantity_mismatches'] > 0 or summary['price_mismatches'] > 0:
            blocks.extend(self._create_discrepancy_blocks(results))
        
        # Timestamp
        blocks.append({
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": f"Comparison completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }]
        })
        
        return blocks

    def _create_summary_text(self, summary: Dict) -> str:
        """Create formatted summary text"""
        
        status_emoji = "✅" if summary['matches'] == summary['total_items'] else "⚠️"
        
        text = f"{status_emoji} *Summary*\n"
        text += f"• Total Items: {summary['total_items']}\n"
        text += f"• Matches: {summary['matches']}\n"
        
        if summary['quantity_mismatches'] > 0:
            text += f"• Quantity Mismatches: {summary['quantity_mismatches']}\n"
            text += f"  Total Quantity Difference: {summary['total_quantity_difference']}\n"
            
        if summary['price_mismatches'] > 0:
            text += f"• Price Mismatches: {summary['price_mismatches']}\n"
            text += f"  Total Price Difference: {self._format_currency(summary['total_price_difference'])}\n"
            
        if summary['missing_items'] > 0:
            text += f"• Missing Items: {summary['missing_items']}\n"
            
        if summary['extra_items'] > 0:
            text += f"• Extra Items: {summary['extra_items']}\n"
            
        return text

    def _create_discrepancy_blocks(self, results: List[Dict]) -> List[Dict]:
        """Create formatted blocks for discrepancies"""
        
        blocks = []
        
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📝 Detailed Discrepancies"
            }
        })
        
        for result in results:
            if result['status'] in ['quantity_mismatch', 'price_mismatch', 'missing', 'extra_item']:
                text = self._format_discrepancy(result)
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text
                    }
                })
        
        return blocks

    def _format_discrepancy(self, result: Dict) -> str:
        """Format a single discrepancy for display"""
        
        status_emoji = {
            'quantity_mismatch': '🔢',
            'price_mismatch': '💰',
            'missing': '❌',
            'extra_item': '➕'
        }.get(result['status'], '❓')
        
        text = f"{status_emoji} *{result['item_code']}*\n"
        text += f"_{result['description']}_\n"
        
        if result['status'] == 'quantity_mismatch':
            text += f"• Offered: {result['offer_quantity']}\n"
            text += f"• Delivered: {result['delivered_quantity']}\n"
            text += f"• Difference: {abs(result['quantity_difference'])}\n"
            
        elif result['status'] == 'price_mismatch':
            text += f"• Offered Price: {self._format_currency(result['offer_price'])}\n"
            text += f"• Invoiced Price: {self._format_currency(result['invoiced_price'])}\n"
            text += f"• Difference: {self._format_currency(abs(result['price_difference']))}\n"
            
        elif result['status'] == 'missing':
            text += f"• Missing from Invoices\n"
            text += f"• Expected Quantity: {result['offer_quantity']}\n"
            
        elif result['status'] == 'extra_item':
            text += f"• Not in Original Offer\n"
            text += f"• Delivered Quantity: {result['delivered_quantity']}\n"
            
        return text

    def _format_path(self, path: str) -> str:
        """Format a file path for display"""
        return path.split('/')[-1]

    def _format_currency(self, amount: Decimal) -> str:
        """Format currency amount"""
        return f"€{amount:,.2f}"

    def send_error(self, error_message: str, details: Optional[str] = None) -> bool:
        """
        Send error notification to Slack
        
        Args:
            error_message: Main error message
            details: Optional detailed error information
        
        Returns:
            bool: True if notification was sent successfully
        """
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Error Alert"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:* {error_message}"
                    }
                }
            ]
            
            if details:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Details:*\n```{details}```"
                    }
                })
            
            response = self.session.post(
                self.config.webhook_url,
                json={
                    "channel": self.config.channel,
                    "blocks": blocks
                }
            )
            
            if response.status_code != 200:
                logging.error(f"Error sending error notification to Slack: {response.text}")
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Error sending error notification to Slack: {str(e)}")
            return False
