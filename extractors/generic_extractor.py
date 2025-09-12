"""
Generic transaction extractor
Fallback for unknown bank formats
"""
from typing import Dict
from .base_extractor import BaseExtractor
import logging

logger = logging.getLogger(__name__)

class GenericExtractor(BaseExtractor):
    """Generic extractor for unknown bank formats"""
    
    def __init__(self):
        patterns = {
            'transaction_id': [
                r'(?:Transaction|Txn|Ref|Reference|ID)(?:\s+)?(?:ID|No|Number|:)[:\s]*([A-Z0-9]{6,})',
                r'(?:^|\s)([A-Z0-9]{8,})(?:\s|$)',  # Any 8+ alphanumeric string
                r'ID[:\s]*([A-Z0-9]+)',
                r'REF[:\s]*([A-Z0-9]+)',
            ],
            'amount': [
                r'([\d,]+(?:\.\d{2})?)\s*ETB',
                r'ETB[:\s]*([\d,]+(?:\.\d{2})?)',
                r'Amount[:\s]*([\d,]+(?:\.\d{2})?)',
                r'Total[:\s]*([\d,]+(?:\.\d{2})?)',
                r'([\d,]+\.\d{2})',  # Any decimal amount
            ],
            'date': [
                r'(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2})',
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(\d{4}-\d{2}-\d{2})',
            ],
            'payer_name': [
                r'(?:From|Payer|Sender|Name)[:\s]+([A-Z][A-Z\s]{2,})',
                r'(?:Customer|Account\s+Holder)[:\s]+([A-Z][A-Z\s]{2,})',
            ],
            'receiver': [
                r'(?:To|Receiver|Beneficiary)[:\s]+([A-Z][A-Z\s]{2,})',
                r'(?:Beneficiary\s+name)[:\s]+([A-Z][A-Z\s]{2,})',
            ],
            'account': [
                r'(?:Account|Acc)[:\s]*(\d+[\*\-]*\d*)',
                r'Account\s+(?:No|Number)[:\s]*(\d+[\*\-]*\d*)',
            ]
        }
        super().__init__("Generic Bank", patterns)
    
    def can_handle(self, url: str, text: str = "") -> bool:
        """Generic extractor can handle any transaction as fallback"""
        # Only use as fallback if we find some transaction indicators
        transaction_indicators = [
            'transaction' in text.lower(),
            'amount' in text.lower(),
            'etb' in text.lower(),
            'bank' in text.lower(),
            'transfer' in text.lower(),
        ]
        
        return sum(transaction_indicators) >= 2  # At least 2 indicators
    
    def extract(self, text: str, url: str = "") -> Dict:
        """Extract generic transaction data"""
        logger.info(f"[Generic] Extracting transaction data from text length: {len(text)}")
        
        extracted_data = {}
        
        # Extract all fields using patterns
        for field_name in self.patterns.keys():
            value = self._extract_field(text, field_name)
            if value:
                extracted_data[field_name] = value
        
        # Standard mapping
        result = {
            'transaction_id': extracted_data.get('transaction_id'),
            'amount': extracted_data.get('amount'),
            'date': extracted_data.get('date'),
            'payer_name': extracted_data.get('payer_name'),
            'receiver': extracted_data.get('receiver'),
            'account': extracted_data.get('account'),
            'payment_method': 'Bank Transfer',
            'status': 'Completed',
        }
        
        # Clean up amount (remove commas)
        if result.get('amount'):
            result['amount'] = result['amount'].replace(',', '')
        
        return self._format_result(result, text)
