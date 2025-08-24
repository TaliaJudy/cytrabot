import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import requests
import random

TOKEN = "8407032246:AAFBcewVBGxRRv8P2XKIUaHSXYh6kxvZeiQ"

# --- Email Settings ---
EMAIL_USER = "yourgmail@gmail.com"       
EMAIL_PASS = "YOUR_APP_PASSWORD"         
EMAIL_RECEIVER = "jackwaikwa1@gmail.com" 

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
    "Where are you located?": "📍 Main Street 123, YourCity."
}

# --- Email Function ---
def send_email(order_text, customer_id, attachment=None, attachment_name="file.png"):
    try:
        subject = "🛒 New Order / Generated Image!"
        body = f"User {customer_id} created:\n\n{order_text}"
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        if attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.getvalue())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={attachment_name}')
            msg.attach(part)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_RECEIVER, msg.as_string())
        print("📧 Email sent successfully")
    except Exception as e:
        print("❌ Email failed:", e)

# --- Telegraph Upload Function ---
def upload_to_telegraph(file_path):
    url = "https://telegra.ph/upload"
    with open(file_path, "rb") as f:
        response = requests.post(url, files={"file": ("file", f, "image/jpeg")})
    result = response.json()
    if "error" in result[0]:
        return None
    return "https://telegra.ph" + result[0]["src"]

# --- Generate gradient background ---
def gradient_background(width=600, height=200):
    img = Image.new("RGB", (width, height), "#000000")
    draw = ImageDraw.Draw(img)
    start_color = tuple(random.randint(0, 255) for _ in range(3))
    end_color = tuple(random.randint(0, 255) for _ in range(3))
    for i in range(height):
        ratio = i / height
        r = int(start_color[0] * (1-ratio) + end_color[0]*ratio)
        g = int(start_color[1] * (1-ratio) + end_color[1]*ratio)
        b = int(start_color[2] * (1-ratio) + end_color[2]*ratio)
        draw.line([(0,i),(width,i)], fill=(r,g,b))
    return img

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
        f"👋 Welcome to *{BUSINESS_NAME}*!\n\n"
        "✨ Fun commands:\n"
        "`/fonts YourText` → Stylish text\n"
        "`/namepic YourName` → Custom name picture\n"
        "`/emoji Combine emojis` → Emoji combiner\n"
        "Or send any photo → I’ll convert it to a URL!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# --- Catalog ---
async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    catalog_text = "📦 *Products:*\n\n"
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
        customer_id = update.message.from_user.username or update.message.from_user.id
        context.user_data["ordering"] = False
        send_email(order_details, customer_id)
        await update.message.reply_text(
            f"✅ Order received:\n\n{order_details}\n"
            f"Our team will contact you soon at {PHONE}.\n"
            f"💳 Proceed with payment using 'Pay Now'."
        )

# --- FAQ ---
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    faq_text = "❓ *FAQs:*\n\n"
    for q, a in FAQS.items():
        faq_text += f"➡️ {q}\n{a}\n\n"
    await query.edit_message_text(faq_text, parse_mode="Markdown")

# --- Contact ---
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    contact_text = (
        f"📞 Contact Info:\n\n"
        f"🌐 Website: {WEBSITE}\n"
        f"📱 Phone: {PHONE}\n"
        f"📧 Email: {EMAIL}\n"
        f"📸 Instagram: {INSTAGRAM}\n"
    )
    await query.edit_message_text(contact_text)

# --- Payment ---
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(PAYMENT_INSTRUCTIONS, parse_mode="Markdown")

# --- Fun: Fonts ---
async def fonts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Usage: `/fonts YourText`", parse_mode="Markdown")
        return
    text = " ".join(context.args)
    fonts = [
        text.upper(),
        text.lower(),
        f"✨ {text} ✨",
        f"🅱️ {text.replace('a','🅰️').replace('e','3')}",
        f"•·.·´¯`·.·• {text} •·.·´¯`·.·•",
        f"💎 {text} 💎",
        f"🌟 {text} 🌟"
    ]
    await update.message.reply_text("🎨 *Stylish Versions:*\n\n" + "\n".join(fonts), parse_mode="Markdown")

# --- Fun: Name Picture with gradient + email ---
async def namepic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Usage: `/namepic YourName`", parse_mode="Markdown")
        return
    name = " ".join(context.args)
    img = gradient_background()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    w, h = draw.textsize(name, font=font)
    draw.text(((img.width-w)/2,(img.height-h)/2), name, font=font, fill=(255,255,255))

    bio = io.BytesIO()
    bio.name = "namepic.png"
    img.save(bio, "PNG")
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption=f"🖼️ Name pic: {name}")
    customer_id = update.message.from_user.username or update.message.from_user.id
    send_email(f"Generated name pic: {name}", customer_id, attachment=bio)

# --- Fun: Emoji Combiner ---
async def emoji_combiner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Usage: `/emoji 😄 🚀 🎉`", parse_mode="Markdown")
        return
    emojis = "".join(context.args)
    await update.message.reply_text(f"✨ Combined emojis:\n{emojis}")

# --- Fun: Photo → URL ---
async def photo_to_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "temp.jpg"
    await file.download_to_drive(file_path)
    link = upload_to_telegraph(file_path)
    if link:
        await update.message.reply_text(f"✅ Your photo URL:\n{link}")
    else:
        await update.message.reply_text("❌ Upload failed.")

# --- Admin Broadcast ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == 123456789:  
        msg = update.message.text.replace("/broadcast ", "")
        for user in context.bot_data.get("subscribers", []):
            try:
                await context.bot.send_message(chat_id=user, text=f"📢 Announcement:\n{msg}")
            except:
                pass
        await update.message.reply_text("✅ Broadcast sent.")
    else:
        await update.message.reply_text("🚫 Not authorized.")

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
    app.add_handler(CommandHandler("fonts", fonts))
    app.add_handler(CommandHandler("namepic", namepic))
    app.add_handler(CommandHandler("emoji", emoji_combiner))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler(filters.PHOTO, photo_to_url))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))
    app.add_handler(MessageHandler(filters.ALL, save_user))
    app.add_handler(CallbackQueryHandler(catalog, pattern="catalog"))
    app.add_handler(CallbackQueryHandler(order, pattern="order"))
    app.add_handler(CallbackQueryHandler(faq, pattern="faq"))
    app.add_handler(CallbackQueryHandler(pay, pattern="pay"))
    app.add_handler(CallbackQueryHandler(contact, pattern="contact"))
    print("🤖 Superbot with all features running...")
    app.run_polling()

if __name__ == "__main__":
    main()
