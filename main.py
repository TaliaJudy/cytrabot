from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

TOKEN = "YOUR_BOT_TOKEN"

# --- Business Data ---
BUSINESS_NAME = "Waikwa Business Bot"
WEBSITE = "https://waikwa.vercel.app"
PHONE = "+254715155196"
INSTAGRAM = "https://instagram.com/cytra_k9"
EMAIL = "jackwaikwa1@gmail.com"
PAYMENT_INSTRUCTIONS = (
    "💳 *Payment Options:*\n\n"
    "📱 M-Pesa: Send payment to +254715155196\n"
    "🌐 Website: https://waikwa.vercel.app\n"
    "📧 Email confirmation: jackwaikwa1@gmail.com\n\n"
    "After payment, please send us a screenshot here."
)

PRODUCTS = {
    "Product A": 49,
    "Product B": 79,
    "Product C": 120
}

FAQS = {
    "What are your working hours?": "⏰ We are open from 9 AM - 6 PM, Mon-Sat.",
    "Do you provide delivery?": "🚚 Yes, we deliver within 3-5 business days.",
    "Where are you located?": "📍 We are located at Main Street 123, YourCity."
}

# --- Start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📂 View Products", callback_data="catalog")],
        [InlineKeyboardButton("🛒 Place Order", callback_data="order")],
        [InlineKeyboardButton("❓ FAQs", callback_data="faq")],
        [InlineKeyboardButton("💳 Pay Now", callback_data="pay")],
        [InlineKeyboardButton("📞 Contact Us", callback_data="contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Welcome to *{BUSINESS_NAME}*! \n\nChoose an option below:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# --- Catalog ---
async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    catalog_text = "📦 *Our Products:*\n\n"
    for name, price in PRODUCTS.items():
        catalog_text += f"➡️ {name} - ${price}\n"
    await query.edit_message_text(catalog_text, parse_mode="Markdown")

# --- Order ---
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["ordering"] = True
    await query.edit_message_text("🛒 Please type the product name and quantity (e.g., `Product A 2`).")

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("ordering"):
        order_details = update.message.text
        context.user_data["ordering"] = False
        await update.message.reply_text(
            f"✅ Thank you! We received your order:\n\n{order_details}\n\n"
            f"Our team will contact you soon at {PHONE}.\n\n"
            f"Please proceed with payment using '💳 Pay Now' button."
        )

# --- FAQ ---
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    faq_text = "❓ *Frequently Asked Questions:*\n\n"
    for q, a in FAQS.items():
        faq_text += f"➡️ {q}\n{a}\n\n"
    await query.edit_message_text(faq_text, parse_mode="Markdown")

# --- Contact Info ---
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    contact_text = (
        f"📞 Contact Information:\n\n"
        f"🌐 Website: {WEBSITE}\n"
        f"📱 Phone: {PHONE}\n"
        f"📧 Email: {EMAIL}\n"
        f"📸 Instagram: {INSTAGRAM}\n"
    )
    await query.edit_message_text(contact_text)

# --- Payment Instructions ---
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(PAYMENT_INSTRUCTIONS, parse_mode="Markdown")

# --- Admin Broadcast ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == 123456789:  # replace with your Telegram ID
        msg = update.message.text.replace("/broadcast ", "")
        for user in context.bot_data.get("subscribers", []):
            try:
                await context.bot.send_message(chat_id=user, text=f"📢 Announcement:\n{msg}")
            except:
                pass
        await update.message.reply_text("✅ Broadcast sent.")
    else:
        await update.message.reply_text("🚫 You are not authorized.")

async def save_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if "subscribers" not in context.bot_data:
        context.bot_data["subscribers"] = []
    if user_id not in context.bot_data["subscribers"]:
        context.bot_data["subscribers"].append(user_id)

# --- Main ---
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))
    app.add_handler(MessageHandler(filters.ALL, save_user))
    app.add_handler(CallbackQueryHandler(catalog, pattern="catalog"))
    app.add_handler(CallbackQueryHandler(order, pattern="order"))
    app.add_handler(CallbackQueryHandler(faq, pattern="faq"))
    app.add_handler(CallbackQueryHandler(pay, pattern="pay"))
    app.add_handler(CallbackQueryHandler(contact, pattern="contact"))

    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
