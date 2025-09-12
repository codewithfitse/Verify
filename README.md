# NextVerify Telegram Bot 🤖⚡

## Instant Transaction Verification on Telegram!

This Telegram bot brings the power of NextVerify directly to your phone! Send transaction PDFs, images, or URLs and get instant verification results.

## 🚀 Features

### **📱 Mobile-First Design**

- **Instant verification** right in Telegram
- **No app installation** required
- **Works on any device** with Telegram

### **🎯 Three Input Methods:**

1. **📎 PDF URLs** - Just paste any transaction PDF link
2. **📁 PDF Files** - Upload PDF documents directly
3. **📷 Images** - Take photos of receipts for OCR processing

### **⚡ Lightning Fast Processing:**

- **Real-time progress** updates
- **Smart text extraction** from PDFs and images
- **Instant results** with formatted transaction details
- **Error handling** with helpful messages

## 🛠️ Setup Instructions

### 1. Create Your Telegram Bot

1. **Message @BotFather** on Telegram
2. **Send:** `/newbot`
3. **Choose a name:** `NextVerify Bot` (or any name you like)
4. **Choose a username:** `your_nextverify_bot` (must end with 'bot')
5. **Copy the token** you receive (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Install Dependencies

```bash
cd telegram_bot
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**Windows:**

```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**Mac:**

```bash
brew install tesseract
```

**Linux:**

```bash
sudo apt update
sudo apt install tesseract-ocr libtesseract-dev
```

### 4. Set Your Bot Token

**Option A: Environment Variable**

```bash
# Windows
set TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE

# Mac/Linux
export TELEGRAM_BOT_TOKEN=YOUR_TOKEN_HERE
```

**Option B: Edit bot.py**

```python
# Replace this line in bot.py:
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# With your actual token:
BOT_TOKEN = '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
```

### 5. Run the Bot

```bash
python bot.py
```

**That's it!** 🎉 Your bot is now live on Telegram!

## 📱 How to Use

### **Start the Bot:**

1. Find your bot on Telegram (search for the username you chose)
2. Send `/start` to begin
3. The bot will show you a welcome message with instructions

### **Verify Transactions:**

**Method 1: PDF URL**

- Copy any transaction PDF link
- Paste it in the chat with your bot
- Get instant verification results!

**Method 2: Upload PDF**

- Click the 📎 attachment button
- Select "Document"
- Choose your PDF file
- Send it to the bot

**Method 3: Send Photo**

- Take a clear photo of your receipt
- Send the image to the bot
- OCR will extract the transaction data

## 🎯 Bot Commands

- `/start` - Welcome message and quick start
- `/help` - Detailed usage instructions
- `/about` - Information about the bot

## 📊 What the Bot Extracts

✅ **Transaction ID/Reference Numbers**  
✅ **Amounts and Currency (ETB)**  
✅ **Transaction Dates**  
✅ **Payer/Receiver Names**  
✅ **Account Numbers**  
✅ **Payment Status**

## 💡 Tips for Best Results

### **For Images:**

- 📷 Take clear, well-lit photos
- 🔍 Ensure text is readable
- 📱 Hold phone steady
- 💡 Use good lighting

### **For PDFs:**

- 📎 Use direct PDF links (not webpage links)
- 📁 Keep file size under 20MB
- ✅ Ensure PDFs contain readable text

## 🚀 Advanced Features

### **Smart Processing:**

- **Progress indicators** for long operations
- **Error handling** with helpful suggestions
- **File size validation** (20MB limit for PDFs)
- **Format validation** (PDF/image type checking)

### **User-Friendly Interface:**

- **Inline keyboards** for easy navigation
- **Markdown formatting** for beautiful messages
- **Emoji indicators** for different states
- **Clear success/error messages**

## 🔒 Privacy & Security

- **No data storage** - all processing is temporary
- **Secure transmission** via Telegram's encryption
- **Local processing** - your files aren't stored anywhere
- **Open source** - you can see exactly what the code does

## 🛠️ Troubleshooting

### **Bot not responding?**

- Check your token is correct
- Ensure the bot is running (`python bot.py`)
- Verify internet connection

### **OCR not working?**

- Install Tesseract OCR properly
- Check image quality (clear, well-lit)
- Try a different image format

### **PDF processing fails?**

- Verify the PDF URL is direct (not a webpage)
- Check file size is under 20MB
- Ensure PDF contains readable text

## 🚀 Production Deployment

For production use:

1. **Use a VPS or cloud server**
2. **Set up process management** (PM2, systemd)
3. **Configure logging** for monitoring
4. **Set up error alerting**
5. **Use environment variables** for tokens

## 📞 Support

Need help? Here are your options:

1. **Check the logs** when running `python bot.py`
2. **Test with known good files** first
3. **Verify all dependencies** are installed
4. **Check Tesseract installation** with `tesseract --version`

---

**🎉 Enjoy instant transaction verification right in Telegram!**

_Built with ❤️ using Python + Telegram Bot API_
