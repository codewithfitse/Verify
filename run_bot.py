#!/usr/bin/env python3
"""
NextVerify Telegram Bot Launcher
Simple script to run the bot with proper error handling
"""

import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required")
        return False
    
    # Check if bot token is set
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        print("💡 Get your token from @BotFather on Telegram")
        print("💡 Set it with: export TELEGRAM_BOT_TOKEN=your_token_here")
        return False
    
    # Check required modules
    required_modules = [
        'telegram', 'PyPDF2', 'pytesseract', 
        'cv2', 'numpy', 'PIL', 'requests'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    
    # Check Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except Exception:
        print("❌ Tesseract OCR not found!")
        print("💡 Install Tesseract OCR:")
        print("   Windows: choco install tesseract")
        print("   Mac: brew install tesseract") 
        print("   Linux: sudo apt install tesseract-ocr")
        return False
    
    print("✅ All requirements satisfied!")
    return True

def main():
    """Main function to run the bot"""
    print("🚀 NextVerify Telegram Bot Launcher")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Requirements check failed!")
        print("Please fix the issues above and try again.")
        sys.exit(1)
    
    print("\n🤖 Starting NextVerify Telegram Bot...")
    print("✅ Bot is ready! Send /start to begin.")
    print("🛑 Press Ctrl+C to stop the bot")
    print("-" * 40)
    
    # Import and run the bot
    try:
        from bot import main as run_bot
        run_bot()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot crashed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
