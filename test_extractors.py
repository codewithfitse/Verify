"""
Test script for the new extraction system
"""
from extractors.extractor_manager import ExtractorManager

# Test data from the Awash Bank receipt
awash_sample = """
Company Information | Customer Information |
Company Name | : | Awash Bank Share company |
TIN No | : | 0000030100 |
VAT Reg No | : | 17264 |
Customer Name | : | Zerihun Tadesse Tefera |
Account No | : | 01320******600/BANK |
Transaction Time | : | 2025-09-12 10:35:43 AM |
Transaction Type | : | Other Bank Transfer |
Amount | : | 1,000 ETB |
Charge | : | 6 ETB |
Sender Name | : | ZERIHUN TADESSE TEFERA |
Beneficiary name | : | EYASU NIGUSIE TULU |
Beneficiary Account | : | 1000229145898 |
Beneficiary Bank | : | COMMERCIAL BANK OF ETHIOPIA |
Transaction ID | : | E43406CDD679 |
"""

# Test URLs
awash_url = "https://awashpay.awashbank.com:8225/-E43406CDD679-2CQJIP"
cbe_url = "https://apps.cbe.com.et:100/?id=FT252528MLNG86227914"

def test_extractors():
    """Test the extraction system"""
    manager = ExtractorManager()
    
    print("🧪 Testing NextVerify Extraction System\n")
    print("=" * 50)
    
    # Test Awash Bank
    print("\n🏛️ Testing Awash Bank Extractor:")
    print(f"URL: {awash_url}")
    result = manager.extract_transaction_data(awash_sample, awash_url)
    
    print(f"✅ Extractor: {result.get('extractor_used')}")
    print(f"✅ Valid: {result.get('is_valid')}")
    print(f"✅ Transaction ID: {result.get('transaction_id')}")
    print(f"✅ Amount: {result.get('amount')} ETB")
    print(f"✅ Payer: {result.get('payer_name')}")
    print(f"✅ Receiver: {result.get('receiver')}")
    
    # Test CBE URL (without text)
    print("\n🏛️ Testing CBE Extractor:")
    print(f"URL: {cbe_url}")
    result2 = manager.extract_transaction_data("", cbe_url)
    
    print(f"✅ Extractor: {result2.get('extractor_used')}")
    print(f"✅ Can Handle: {result2.get('is_valid')}")
    
    # List supported banks
    print("\n🏛️ Supported Banks:")
    for bank in manager.list_supported_banks():
        print(f"• {bank}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_extractors()
