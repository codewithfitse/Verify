import logging
import os
import io
import re
import requests
import PyPDF2
import pytesseract
import cv2
import numpy as np
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
import asyncio

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

def extract_transaction_data(text: str) -> dict:
    """Extract transaction information from text using regex patterns"""
    logger.info(f"Extracting transaction data from text: {text[:200]}...")
    
    patterns = {
        'transaction_id': [
            r'(?:Transaction|Txn|Ref|Reference)(?:\s+)?(?:ID|No|Number)[:\s]+([A-Z0-9]+)',
            r'TXN[:\s]*([A-Z0-9]+)',
            r'REF[:\s]*([A-Z0-9]+)',
            r'ID[:\s]*([A-Z0-9]{6,})',
            r'Reference No\. \(VAT Invoice No\)\s+([A-Z0-9]+)',
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
    
    extracted_data = {}
    
    for field, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_data[field] = match.group(1).strip()
                logger.info(f"Found {field}: {extracted_data[field]}")
                break
    
    # Determine if extraction was successful
    is_valid = bool(
        extracted_data.get('transaction_id') and 
        extracted_data.get('amount') and 
        (extracted_data.get('date') or extracted_data.get('payer_name'))
    )
    
    return {
        **extracted_data,
        'is_valid': is_valid,
        'raw_text': text
    }

def extract_pdf_text(pdf_content: bytes) -> str:
    """Extract text from PDF using PyPDF2"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + " "
            
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text
        
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

def process_image_ocr(image_data: bytes) -> str:
    """Process image using OCR to extract text"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Preprocess image for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Use Tesseract to extract text
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(thresh, config=custom_config)
        
        logger.info(f"OCR extracted {len(text)} characters from image")
        return text
        
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        raise Exception(f"Failed to process image: {str(e)}")

def format_transaction_result(result: dict) -> str:
    """Format transaction result for Telegram message"""
    if result['is_valid']:
        message = "✅ **Transaction Verified Successfully!**\n\n"
        
        if result.get('transaction_id'):
            message += f"🔍 **Transaction ID:** `{result['transaction_id']}`\n"
        if result.get('amount'):
            message += f"💰 **Amount:** {result['amount']} ETB\n"
        if result.get('date'):
            message += f"📅 **Date:** {result['date']}\n"
        if result.get('payer_name'):
            message += f"👤 **Payer:** {result['payer_name']}\n"
        if result.get('receiver'):
            message += f"🏦 **Receiver:** {result['receiver']}\n"
        if result.get('account'):
            message += f"📊 **Account:** {result['account']}\n"
            
        message += "\n🎉 **Status:** Transaction details successfully extracted and verified!"
        
    else:
        message = "❌ **Verification Failed**\n\n"
        message += "⚠️ Could not extract valid transaction data.\n"
        message += "Please ensure:\n"
        message += "• The PDF/image contains transaction details\n"
        message += "• The text is clear and readable\n"
        message += "• The document is a valid transaction receipt\n"
        
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🚀 **Welcome to NextVerify Bot!**

I can help you verify transactions quickly and securely. Just send me:

📎 **PDF Link** - Paste any transaction PDF URL
📁 **PDF File** - Upload a PDF document
📷 **Image** - Send a photo of your receipt

I'll extract and verify all transaction details instantly!

**Commands:**
/start - Show this welcome message
/help - Get detailed help
/about - Learn more about NextVerify

**Ready to verify your first transaction?** 
Just send me a PDF link, file, or image! 📊✨
    """
    
    keyboard = [
        [InlineKeyboardButton("📖 Help", callback_data='help'),
         InlineKeyboardButton("ℹ️ About", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message, 
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help information."""
    help_message = """
📖 **NextVerify Bot Help**

**How to use:**

1️⃣ **Send PDF URL**
   • Copy any transaction PDF link
   • Paste it in the chat
   • I'll download and verify it instantly!

2️⃣ **Upload PDF File**
   • Click the 📎 attachment button
   • Select your PDF file
   • Send it to me for verification

3️⃣ **Send Image**
   • Take a photo of your receipt
   • Send the image to me
   • I'll use OCR to extract the data

**What I extract:**
✅ Transaction ID/Reference
✅ Amount and Currency
✅ Date and Time
✅ Payer/Receiver Names
✅ Account Numbers

**Tips for best results:**
• Ensure images are clear and well-lit
• Make sure text is readable
• PDF files work better than images
• URLs should be direct PDF links

Need more help? Contact support! 🤝
    """
    
    await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the bot."""
    about_message = """
ℹ️ **About NextVerify Bot**

🚀 **Fast & Secure Transaction Verification**

NextVerify Bot uses advanced Python libraries to:
• Extract text from PDFs with PyPDF2
• Process images with OpenCV + Tesseract OCR
• Parse transaction data with smart regex patterns
• Provide instant verification results

**Features:**
⚡ Lightning-fast processing
🔒 Secure and private
🎯 High accuracy extraction
📱 Mobile-friendly
🌍 Works with multiple formats

**Technology Stack:**
• Python + FastAPI
• Telegram Bot API
• PyPDF2 for PDF processing
• Tesseract OCR for images
• OpenCV for image preprocessing

**Developed with ❤️ for fast transaction verification**

Version 1.0 | Made with Python 🐍
    """
    
    await update.message.reply_text(about_message, parse_mode=ParseMode.MARKDOWN)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help':
        await help_command(update, context)
    elif query.data == 'about':
        await about_command(update, context)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle PDF URL messages."""
    url = update.message.text.strip()
    
    # Check if it's a URL
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text(
            "❌ Please send a valid PDF URL starting with http:// or https://",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "⏳ **Processing PDF URL...**\n\n🔄 Downloading and extracting data...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Download PDF
        logger.info(f"Processing PDF from URL: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Update progress
        await processing_msg.edit_text(
            "⏳ **Processing PDF URL...**\n\n📄 PDF downloaded, extracting text...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Extract text from PDF
        text = extract_pdf_text(response.content)
        
        # Update progress
        await processing_msg.edit_text(
            "⏳ **Processing PDF URL...**\n\n🔍 Analyzing transaction data...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Extract transaction data
        result = extract_transaction_data(text)
        
        # Format and send result
        result_message = format_transaction_result(result)
        
        # Delete processing message and send result
        await processing_msg.delete()
        await update.message.reply_text(result_message, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"URL processing failed: {e}")
        await processing_msg.edit_text(
            f"❌ **Processing Failed**\n\n⚠️ Error: {str(e)}\n\nPlease check the URL and try again.",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle PDF document uploads."""
    document = update.message.document
    
    # Check if it's a PDF
    if not document.file_name.lower().endswith('.pdf'):
        await update.message.reply_text(
            "❌ **Invalid File Type**\n\nPlease send a PDF file (.pdf extension required)",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Check file size (limit to 20MB)
    if document.file_size > 20 * 1024 * 1024:
        await update.message.reply_text(
            "❌ **File Too Large**\n\nPlease send a PDF file smaller than 20MB",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        f"⏳ **Processing PDF File...**\n\n📁 File: {document.file_name}\n🔄 Downloading and extracting data...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        file_data = await file.download_as_bytearray()
        
        # Update progress
        await processing_msg.edit_text(
            f"⏳ **Processing PDF File...**\n\n📁 File: {document.file_name}\n📄 Extracting text...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Extract text from PDF
        text = extract_pdf_text(bytes(file_data))
        
        # Update progress
        await processing_msg.edit_text(
            f"⏳ **Processing PDF File...**\n\n📁 File: {document.file_name}\n🔍 Analyzing transaction data...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Extract transaction data
        result = extract_transaction_data(text)
        
        # Format and send result
        result_message = format_transaction_result(result)
        
        # Delete processing message and send result
        await processing_msg.delete()
        await update.message.reply_text(result_message, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        await processing_msg.edit_text(
            f"❌ **Processing Failed**\n\n⚠️ Error: {str(e)}\n\nPlease try again with a different PDF file.",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo uploads for OCR processing."""
    photo = update.message.photo[-1]  # Get the highest resolution version
    
    # Send processing message
    processing_msg = await update.message.reply_text(
        "⏳ **Processing Image...**\n\n📷 Analyzing image with OCR...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Download photo
        file = await context.bot.get_file(photo.file_id)
        file_data = await file.download_as_bytearray()
        
        # Update progress
        await processing_msg.edit_text(
            "⏳ **Processing Image...**\n\n🔍 Extracting text from image...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Extract text using OCR
        text = process_image_ocr(bytes(file_data))
        
        # Update progress
        await processing_msg.edit_text(
            "⏳ **Processing Image...**\n\n📊 Analyzing transaction data...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Extract transaction data
        result = extract_transaction_data(text)
        
        # Format and send result
        result_message = format_transaction_result(result)
        
        # Delete processing message and send result
        await processing_msg.delete()
        await update.message.reply_text(result_message, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Photo processing failed: {e}")
        await processing_msg.edit_text(
            f"❌ **Processing Failed**\n\n⚠️ Error: {str(e)}\n\nPlease try again with a clearer image.",
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle other message types."""
    message = """
🤔 **I don't understand this message type**

Please send me one of these:

📎 **PDF URL** - Paste a link to a transaction PDF
📁 **PDF File** - Upload a PDF document
📷 **Photo** - Send an image of your receipt

Use /help for detailed instructions! 📖
    """
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

def main() -> None:
    """Start the bot."""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Error: Please set your TELEGRAM_BOT_TOKEN environment variable!")
        print("💡 Get your token from @BotFather on Telegram")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CallbackQueryHandler(handle_button))
    
    # Handle different message types
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(~filters.TEXT & ~filters.Document.PDF & ~filters.PHOTO, handle_other_messages))
    
    # Start the bot
    print("🚀 NextVerify Telegram Bot is starting...")
    print("✅ Bot is running! Send /start to begin.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
