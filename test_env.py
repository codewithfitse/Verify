import os

# Test if environment variable is set
token = os.getenv('TELEGRAM_BOT_TOKEN')

if token:
    # Hide most of the token for security
    masked_token = token[:10] + "..." + token[-10:] if len(token) > 20 else "***"
    print(f"✅ Token found: {masked_token}")
    print("🚀 Ready to run the bot!")
else:
    print("❌ TELEGRAM_BOT_TOKEN not found!")
    print("💡 Set it with:")
    print('   $env:TELEGRAM_BOT_TOKEN="your_token_here"')
