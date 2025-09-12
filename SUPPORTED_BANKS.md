# 🏛️ Supported Banks - NextVerify Bot

NextVerify Bot supports automatic transaction verification for multiple Ethiopian banks with specialized extractors for each bank's format.

## ✅ Fully Supported Banks

### 🏛️ **Awash Bank**

- **URL Pattern:** `awashpay.awashbank.com`
- **Example URL:** `https://awashpay.awashbank.com:8225/-E43406CDD679-2CQJIP`
- **Extracted Data:**
  - ✅ Transaction ID
  - ✅ Amount and Charges
  - ✅ Date and Time
  - ✅ Payer Name
  - ✅ Receiver Name and Account
  - ✅ Receiver Bank
  - ✅ Transaction Type
  - ✅ Branch Information

### 🏛️ **Commercial Bank of Ethiopia (CBE)**

- **URL Pattern:** `apps.cbe.com.et`
- **Example URL:** `https://apps.cbe.com.et:100/?id=FT252528MLNG86227914`
- **Extracted Data:**
  - ✅ Transaction ID (from URL)
  - ✅ Amount
  - ✅ Date
  - ✅ Payer/Receiver Names
  - ✅ Account Information

## 🔄 Generic Support

### 🏛️ **Other Banks**

- **Fallback:** Generic extractor for unknown formats
- **Detection:** Looks for common transaction indicators
- **Extracted Data:**
  - ✅ Basic transaction information
  - ✅ Amount in ETB
  - ✅ Transaction IDs
  - ✅ Dates and names (when available)

## 🚀 How It Works

1. **Smart Detection:** Bot analyzes the URL and content to identify the bank
2. **Specialized Extraction:** Uses bank-specific patterns for maximum accuracy
3. **Rich Data:** Extracts comprehensive transaction details
4. **Fallback Support:** Generic extractor handles unknown formats

## 📈 Adding New Banks

The system is designed to be easily extensible:

```python
# Example: Adding Dashen Bank support
class DashenExtractor(BaseExtractor):
    def can_handle(self, url, text):
        return 'dashenbank.com' in url.lower()

    def extract(self, text, url):
        # Bank-specific extraction patterns
        pass

# Automatically integrated into the system
extractor_manager.add_extractor(DashenExtractor())
```

## 🧪 Testing

Each bank extractor is thoroughly tested with real transaction data to ensure:

- ✅ Accurate data extraction
- ✅ Proper format handling
- ✅ Error resilience
- ✅ SSL certificate handling

## 💡 Usage Tips

- **Direct PDF URLs work best** for maximum data extraction
- **Clear, readable text** improves extraction accuracy
- **Supported bank formats** provide the richest transaction details
- **Generic fallback** handles most other bank formats

---

**Need support for a new bank?** Send us a sample transaction receipt and we'll add specialized support! 🚀
