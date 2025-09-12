"""
Awash Bank transaction extractor
Handles receipts from awashpay.awashbank.com
"""
from typing import Dict
from .base_extractor import BaseExtractor
import logging

logger = logging.getLogger(__name__)

class AwashExtractor(BaseExtractor):
    """Extractor for Awash Bank transactions"""
    
    def __init__(self):
        patterns = {
            'transaction_id': [
                r'Transaction ID\s*[:\|]*\s*([A-Z0-9]+)',
                r'Transaction ID\s*\|\s*:\s*\|\s*([A-Z0-9]+)',
                r'Transaction ID.*?([A-Z0-9]{8,})',
                r'ID\s*[:\|]*\s*([A-Z0-9]+)',
                r'([A-Z0-9]{8,})',  # Any 8+ alphanumeric (from URL)
            ],
            'amount': [
                r'Amount\s*[:\|]*\s*([\d,]+(?:\.\d{2})?)\s*ETB',
                r'Amount\s*\|\s*:\s*\|\s*([\d,]+(?:\.\d{2})?)\s*ETB',
                r'([\d,]+(?:\.\d{2})?)\s*ETB',
                r'Amount.*?([\d,]+)',  # More flexible amount matching
            ],
            'date': [
                r'Transaction Time\s*:\s*(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)?)',
                r'Transaction Time\s*\|\s*:\s*\|\s*(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)?)',
                r'(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
            ],
            'payer_name': [
                r'Sender Name\s*:\s*([A-Z\s]+)',
                r'Sender Name\s*\|\s*:\s*\|\s*([A-Z\s]+)',
                r'Customer Name\s*:\s*([A-Z\s]+)',
                r'Customer Name\s*\|\s*:\s*\|\s*([A-Z\s]+)',
            ],
            'receiver': [
                r'Beneficiary name\s*:\s*([A-Z\s]+)',
                r'Beneficiary name\s*\|\s*:\s*\|\s*([A-Z\s]+)',
                r'Beneficiary\s*:\s*([A-Z\s]+)',
            ],
            'sender_account': [
                r'Sender Account\s*:\s*([0-9\*]+)',
                r'Sender Account\s*\|\s*:\s*\|\s*([0-9\*]+)',
                r'Account No\s*:\s*([0-9\*\/A-Z]+)',
                r'Account No\s*\|\s*:\s*\|\s*([0-9\*\/A-Z]+)',
            ],
            'receiver_account': [
                r'Beneficiary Account\s*:\s*([0-9]+)',
                r'Beneficiary Account\s*\|\s*:\s*\|\s*([0-9]+)',
            ],
            'receiver_bank': [
                r'Beneficiary Bank\s*:\s*([A-Z\s]+)',
                r'Beneficiary Bank\s*\|\s*:\s*\|\s*([A-Z\s]+)',
            ],
            'transaction_type': [
                r'Transaction Type\s*:\s*([A-Z\s]+)',
                r'Transaction Type\s*\|\s*:\s*\|\s*([A-Z\s]+)',
            ],
            'charge': [
                r'Charge\s*:\s*([\d,]+(?:\.\d{2})?)\s*ETB',
                r'Charge\s*\|\s*:\s*\|\s*([\d,]+(?:\.\d{2})?)\s*ETB',
            ],
            'branch': [
                r'Branch\s*:\s*([A-Z\s]+)',
                r'Branch\s*\|\s*:\s*\|\s*([A-Z\s]+)',
            ]
        }
        super().__init__("Awash Bank", patterns)
    
    def can_handle(self, url: str, text: str = "") -> bool:
        """Check if this is an Awash Bank transaction"""
        awash_indicators = [
            'awashpay.awashbank.com' in url.lower(),
            'awash bank' in text.lower(),
            'awash bank share company' in text.lower(),
            'transaction time' in text.lower() and 'beneficiary' in text.lower(),
        ]
        
        return any(awash_indicators)
    
    def extract(self, text: str, url: str = "") -> Dict:
        """Extract Awash Bank transaction data"""
        logger.info(f"[Awash Bank] Extracting transaction data from text length: {len(text)}")
        
        extracted_data = {}
        
        # Extract all fields using patterns
        for field_name in self.patterns.keys():
            value = self._extract_field(text, field_name)
            if value:
                extracted_data[field_name] = value
        
        # If no transaction ID found in text, try to extract from URL
        if not extracted_data.get('transaction_id') and url:
            import re
            # Extract from Awash URL format: -E43406CDD679-
            url_match = re.search(r'-([A-Z0-9]+)-', url)
            if url_match:
                extracted_data['transaction_id'] = url_match.group(1)
                logger.info(f"[Awash Bank] Found transaction ID in URL: {extracted_data['transaction_id']}")
        
        # Map to standard field names for compatibility
        result = {
            'transaction_id': extracted_data.get('transaction_id'),
            'amount': extracted_data.get('amount'),
            'date': extracted_data.get('date'),
            'payer_name': extracted_data.get('payer_name'),
            'receiver': extracted_data.get('receiver'),
            'account': extracted_data.get('sender_account'),
            'receiver_account': extracted_data.get('receiver_account'),
            'receiver_bank': extracted_data.get('receiver_bank'),
            'transaction_type': extracted_data.get('transaction_type'),
            'charge': extracted_data.get('charge'),
            'branch': extracted_data.get('branch'),
            'payment_method': 'Bank Transfer',
            'status': 'Completed',
        }
        
        # Clean up amount (remove commas)
        if result.get('amount'):
            result['amount'] = result['amount'].replace(',', '')
        
        return self._format_result(result, text)
