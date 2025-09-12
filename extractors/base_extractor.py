"""
Base extractor class for transaction data extraction
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    """Base class for all transaction extractors"""
    
    def __init__(self, bank_name: str, patterns: Dict[str, List[str]]):
        self.bank_name = bank_name
        self.patterns = patterns
    
    @abstractmethod
    def can_handle(self, url: str, text: str = "") -> bool:
        """Check if this extractor can handle the given URL/text"""
        pass
    
    @abstractmethod
    def extract(self, text: str, url: str = "") -> Dict:
        """Extract transaction data from text"""
        pass
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a specific field using regex patterns"""
        if field_name not in self.patterns:
            return None
            
        for pattern in self.patterns[field_name]:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                result = match.group(1).strip()
                logger.info(f"[{self.bank_name}] Found {field_name}: {result}")
                return result
        
        return None
    
    def _format_result(self, extracted_data: Dict, text: str) -> Dict:
        """Format the extraction result"""
        # More lenient validation - just need transaction_id and amount
        is_valid = bool(
            extracted_data.get('transaction_id') and 
            extracted_data.get('amount')
        )
        
        return {
            **extracted_data,
            'is_valid': is_valid,
            'bank_name': self.bank_name,
            'raw_text': text
        }
