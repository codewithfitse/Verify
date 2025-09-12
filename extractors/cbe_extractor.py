"""
Commercial Bank of Ethiopia (CBE) transaction extractor
Handles receipts from CBE systems
"""
from typing import Dict
from .base_extractor import BaseExtractor
import logging

logger = logging.getLogger(__name__)

class CBEExtractor(BaseExtractor):
    """Extractor for CBE transactions"""
    
    def __init__(self):
        patterns = {
            'transaction_id': [
                r'(?:Transaction|Txn|Ref|Reference)(?:\s+)?(?:ID|No|Number)[:\s]+([A-Z0-9]+)',
                r'TXN[:\s]*([A-Z0-9]+)',
                r'REF[:\s]*([A-Z0-9]+)',
                r'ID[:\s]*([A-Z0-9]{6,})',
                r'Reference No\. \(VAT Invoice No\)\s+([A-Z0-9]+)',
                r'FT(\d+[A-Z0-9]+)',  # CBE format like FT252528MLNG86227914
            ],
            'amount': [
                r'(?:Amount|Total|Sum)[:\s]+([\d,]+\.?\d*)',
                r'ETB[:\s]+([\d,]+\.?\d*)',
                r'([\d,]+\.?\d*)\s*ETB',
                r'Transferred Amount\s+([\d,]+\.\d{2})\s+ETB',
            ],
            'date': [
                r'(?:Date|Time)[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'Payment Date & Time\s+(\d{1,2}\/\d{1,2}\/\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
            ],
            'payer_name': [
                r'(?:From|Payer|Name)[:\s]+([A-Z\s]+)',
                r'(?:Account\s+Holder)[:\s]+([A-Z\s]+)',
                r'Payer\s+([A-Z\s]+)',
            ],
            'receiver': [
                r'(?:To|Receiver|Beneficiary)[:\s]+([A-Z\s]+)',
                r'Receiver\s+([A-Z\s]+)',
            ],
            'account': [
                r'(?:Account|Acc)[:\s]*(\d+[\*\-]*\d*)',
                r'Account\s+(\d+\*+\d+)',
            ]
        }
        super().__init__("Commercial Bank of Ethiopia", patterns)
    
    def can_handle(self, url: str, text: str = "") -> bool:
        """Check if this is a CBE transaction"""
        cbe_indicators = [
            'apps.cbe.com.et' in url.lower(),
            'commercial bank of ethiopia' in text.lower(),
            'cbe' in text.lower(),
            'FT' in url and len([c for c in url if c.isdigit()]) > 8,  # CBE format
        ]
        
        return any(cbe_indicators)
    
    def extract(self, text: str, url: str = "") -> Dict:
        """Extract CBE transaction data"""
        logger.info(f"[CBE] Extracting transaction data from text length: {len(text)}")
        
        extracted_data = {}
        
        # Extract all fields using patterns
        for field_name in self.patterns.keys():
            value = self._extract_field(text, field_name)
            if value:
                extracted_data[field_name] = value
        
        # If no transaction ID found in text, try to extract from URL
        if not extracted_data.get('transaction_id') and url:
            import re
            url_match = re.search(r'id=([A-Z0-9]+)', url)
            if url_match:
                extracted_data['transaction_id'] = url_match.group(1)
                logger.info(f"[CBE] Found transaction ID in URL: {extracted_data['transaction_id']}")
        
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
