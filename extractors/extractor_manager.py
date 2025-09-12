"""
Manager for handling multiple bank extractors
"""
from typing import Dict, List, Optional
import logging
from .awash_extractor import AwashExtractor
from .cbe_extractor import CBEExtractor
from .generic_extractor import GenericExtractor
from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class ExtractorManager:
    """Manages multiple bank extractors and selects the best one"""
    
    def __init__(self):
        self.extractors: List[BaseExtractor] = [
            AwashExtractor(),
            CBEExtractor(),
            GenericExtractor(),  # Keep as fallback
        ]
        logger.info(f"Initialized ExtractorManager with {len(self.extractors)} extractors")
    
    def extract_transaction_data(self, text: str, url: str = "") -> Dict:
        """Extract transaction data using the best matching extractor"""
        logger.info(f"Extracting transaction data from URL: {url[:50]}...")
        
        # Find the best extractor
        best_extractor = self._find_best_extractor(url, text)
        
        if best_extractor:
            logger.info(f"Using {best_extractor.bank_name} extractor")
            result = best_extractor.extract(text, url)
            
            # Add extractor info to result
            result['extractor_used'] = best_extractor.bank_name
            
            return result
        
        # Fallback if no extractor found
        logger.warning("No suitable extractor found, using generic patterns")
        return {
            'is_valid': False,
            'error': 'No suitable extractor found for this transaction format',
            'extractor_used': 'None',
            'raw_text': text
        }
    
    def _find_best_extractor(self, url: str, text: str) -> Optional[BaseExtractor]:
        """Find the best extractor for the given URL and text"""
        
        # First, try specific bank extractors (not generic)
        for extractor in self.extractors[:-1]:  # Exclude generic
            if extractor.can_handle(url, text):
                logger.info(f"Found specific extractor: {extractor.bank_name}")
                return extractor
        
        # If no specific extractor found, try generic as fallback
        generic_extractor = self.extractors[-1]
        if generic_extractor.can_handle(url, text):
            logger.info("Using generic extractor as fallback")
            return generic_extractor
        
        return None
    
    def add_extractor(self, extractor: BaseExtractor):
        """Add a new extractor to the manager"""
        # Insert before generic extractor (keep generic as last)
        self.extractors.insert(-1, extractor)
        logger.info(f"Added new extractor: {extractor.bank_name}")
    
    def list_supported_banks(self) -> List[str]:
        """Get list of supported bank names"""
        return [extractor.bank_name for extractor in self.extractors[:-1]]  # Exclude generic
