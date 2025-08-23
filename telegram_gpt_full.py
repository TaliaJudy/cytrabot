import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Load environment variables from .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is used"""
    await update.message.reply_text("🤖 Hello! I’m your AI-powered bot. Ask me anything!")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages and reply with OpenAI"""
    user_message = update.message.text

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4o" if you want richer responses
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
        )

        bot_reply = response.choices[0].message.content
        await update.message.reply_text(bot_reply)

    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        await update.message.reply_text("⚠️ Sorry, something went wrong.")


# --- Main ---
def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("❌ TELEGRAM_TOKEN not found in environment")

    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY not found in environment")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logging.info("🚀 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
    
