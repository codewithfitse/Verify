# 🚀 Quick Setup - NextVerify Telegram Bot

## Step 1: Create Your Telegram Bot (2 minutes)

1. **Open Telegram** and search for `@BotFather`
2. **Send:** `/newbot`
3. **Bot Name:** `NextVerify Bot` (or any name you like)
4. **Bot Username:** `your_nextverify_bot` (must end with 'bot')
5. **Copy the token** you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Set Your Token (30 seconds)

**Edit the file `bot_simple.py` and replace:**

```python
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
```

**With your actual token:**

```python
BOT_TOKEN = '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
```

## Step 3: Run the Bot (30 seconds)

```bash
python bot_simple.py
```

**That's it! Your bot is live!** 🎉

## Step 4: Test Your Bot

1. **Find your bot** on Telegram (search for the username you chose)
2. **Send:** `/start`
3. **Test with a PDF URL** or upload a PDF file

## 🎯 What Works Right Now:

✅ **PDF URL Processing** - Paste any transaction PDF link  
✅ **PDF File Upload** - Upload PDF documents directly  
✅ **Transaction Data Extraction** - ID, Amount, Date, Names, etc.  
✅ **Beautiful Results** - Formatted with emojis and markdown

## 🔜 Coming Soon:

📷 **Image OCR** - Will be added once OpenCV and Tesseract are installed

## 💡 Tips:

- **Use direct PDF links** (not webpage links)
- **Keep PDF files under 20MB**
- **Test with bank transaction receipts**

**Enjoy your lightning-fast transaction verification bot!** ⚡🤖
