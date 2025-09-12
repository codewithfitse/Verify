import logging
import os
import io
import re
import requests
import PyPDF2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from dotenv import load_dotenv
from extractors.extractor_manager import ExtractorManager

# Load environment variables from .env file
load_dotenv()

# Initialize the extraction manager
extractor_manager = ExtractorManager()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration - REPLACE WITH YOUR ACTUAL TOKEN
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Transaction extraction is now handled by the ExtractorManager

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

def extract_html_text(html_content: bytes) -> str:
    """Extract text from HTML content"""
    try:
        from bs4 import BeautifulSoup
        
        # Decode HTML content
        html_text = html_content.decode('utf-8', errors='ignore')
        
        # Parse HTML
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        logger.info(f"Extracted {len(text)} characters from HTML")
        return text
        
    except Exception as e:
        logger.error(f"HTML extraction failed: {e}")
        raise Exception(f"Failed to extract text from HTML: {str(e)}")

def extract_content_text(content: bytes, content_type: str) -> str:
    """Extract text from content - handles both PDF and HTML"""
    content_type = content_type.lower()
    
    logger.info(f"Processing content type: {content_type}")
    
    # Try PDF first
    if 'pdf' in content_type or content.startswith(b'%PDF'):
        try:
            return extract_pdf_text(content)
        except Exception as e:
            logger.warning(f"PDF extraction failed, trying HTML: {e}")
    
    # Try HTML
    if 'html' in content_type or b'<html' in content.lower() or b'<!doctype' in content.lower():
        try:
            return extract_html_text(content)
        except Exception as e:
            logger.warning(f"HTML extraction failed: {e}")
    
    # Fallback: treat as plain text
    try:
        text = content.decode('utf-8', errors='ignore')
        logger.info(f"Extracted {len(text)} characters as plain text")
        return text
    except Exception as e:
        logger.error(f"All content extraction methods failed: {e}")
        raise Exception("Failed to extract text from content")

def format_transaction_result(result: dict) -> str:
    """Format transaction result for Telegram message"""
    if result['is_valid']:
        bank_name = result.get('extractor_used', 'Unknown Bank')
        message = f"✅ **Transaction Verified Successfully!**\n"
        message += f"🏛️ **Bank:** {bank_name}\n\n"
        
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
        if result.get('receiver_account'):
            message += f"📊 **Receiver Account:** {result['receiver_account']}\n"
        if result.get('receiver_bank'):
            message += f"🏛️ **Receiver Bank:** {result['receiver_bank']}\n"
        if result.get('transaction_type'):
            message += f"📋 **Type:** {result['transaction_type']}\n"
        if result.get('charge'):
            message += f"💳 **Charge:** {result['charge']} ETB\n"
        if result.get('branch'):
            message += f"🏢 **Branch:** {result['branch']}\n"
            
        message += "\n🎉 **Status:** Transaction details successfully extracted and verified!"
        
    else:
        message = "❌ **Verification Failed**\n\n"
        error_msg = result.get('error', 'Could not extract valid transaction data')
        message += f"⚠️ {error_msg}\n\n"
        message += "**Supported Banks:**\n"
        supported_banks = extractor_manager.list_supported_banks()
        for bank in supported_banks:
            message += f"• {bank}\n"
        message += "\n**Tips:**\n"
        message += "• Ensure the PDF contains transaction details\n"
        message += "• Check that the document is from a supported bank\n"
        message += "• Make sure the text is clear and readable\n"
        
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🚀 **Welcome to NextVerify Bot!**

I can help you verify transactions quickly and securely. Send me:

📎 **PDF Link** - Paste any transaction PDF URL
📁 **PDF File** - Upload a PDF document
📷 **Image** - Coming soon! (OCR support)

I'll extract and verify all transaction details instantly!

**Commands:**
/start - Show this welcome message
/help - Get detailed help
/about - Learn more about NextVerify

**Ready to verify your first transaction?** 
Just send me a PDF link or file! 📊✨
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

**What I extract:**
✅ Transaction ID/Reference
✅ Amount and Currency
✅ Date and Time
✅ Payer/Receiver Names
✅ Account Numbers

**Tips for best results:**
• PDF files work best
• URLs should be direct PDF links
• Ensure PDFs contain readable text

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
• Parse transaction data with smart regex patterns
• Provide instant verification results

**Features:**
⚡ Lightning-fast processing
🔒 Secure and private
🎯 High accuracy extraction
📱 Mobile-friendly
🌍 Works with multiple formats

**Technology Stack:**
• Python + Telegram Bot API
• PyPDF2 for PDF processing
• Smart regex patterns for data extraction

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
        # Handle SSL issues with verify=False for problematic certificates
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        # Update progress
        await processing_msg.edit_text(
            "⏳ **Processing PDF URL...**\n\n📄 PDF downloaded, extracting text...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Try to extract text - could be PDF or HTML
        text = extract_content_text(response.content, response.headers.get('content-type', ''))
        
        # Update progress
        await processing_msg.edit_text(
            "⏳ **Processing PDF URL...**\n\n🔍 Analyzing transaction data...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Extract transaction data using the appropriate extractor
        result = extractor_manager.extract_transaction_data(text, url)
        
        # Format and send result
        result_message = format_transaction_result(result)
        
        # Delete processing message and send result
        await processing_msg.delete()
        await update.message.reply_text(result_message, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"URL processing failed: {e}")
        error_msg = str(e)
        # Escape markdown characters in error message
        error_msg = error_msg.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)')
        try:
            await processing_msg.edit_text(
                f"❌ **Processing Failed**\n\n⚠️ Error: {error_msg}\n\nPlease check the URL and try again.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            # Fallback without markdown if still failing
            await processing_msg.edit_text(
                f"❌ Processing Failed\n\nError: {str(e)}\n\nPlease check the URL and try again."
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
        
        # Extract transaction data using the appropriate extractor
        result = extractor_manager.extract_transaction_data(text, "")
        
        # Format and send result
        result_message = format_transaction_result(result)
        
        # Delete processing message and send result
        await processing_msg.delete()
        await update.message.reply_text(result_message, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        error_msg = str(e)
        # Escape markdown characters in error message
        error_msg = error_msg.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)')
        try:
            await processing_msg.edit_text(
                f"❌ **Processing Failed**\n\n⚠️ Error: {error_msg}\n\nPlease try again with a different PDF file.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            # Fallback without markdown if still failing
            await processing_msg.edit_text(
                f"❌ Processing Failed\n\nError: {str(e)}\n\nPlease try again with a different PDF file."
            )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo uploads - OCR coming soon."""
    await update.message.reply_text(
        "📷 **Image OCR Coming Soon!**\n\n"
        "Image processing with OCR will be available in the next update.\n\n"
        "For now, please use:\n"
        "📎 **PDF URLs** - Paste transaction PDF links\n"
        "📁 **PDF Files** - Upload PDF documents\n\n"
        "Thank you for your patience! 🙏",
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle other message types."""
    message = """
🤔 **I don't understand this message type**

Please send me one of these:

📎 **PDF URL** - Paste a link to a transaction PDF
📁 **PDF File** - Upload a PDF document
📷 **Photo** - Coming soon with OCR support!

Use /help for detailed instructions! 📖
    """
    
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def main() -> None:
    """Start the bot."""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Error: Please set your TELEGRAM_BOT_TOKEN!")
        print("💡 Get your token from @BotFather on Telegram")
        print("💡 Edit this file and replace YOUR_BOT_TOKEN_HERE with your actual token")
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
    
    # Initialize the bot
    await application.initialize()
    await application.start()
    
    # Start the bot
    print("🚀 NextVerify Telegram Bot is starting...")
    print("✅ Bot is running! Send /start to begin.")
    print("🔧 Note: Image OCR support coming soon!")
    
    # Run the bot
    await application.updater.start_polling()
    
    # Keep the bot running
    try:
        import asyncio
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
