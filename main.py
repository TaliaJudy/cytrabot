from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from PIL import Image, ImageDraw, ImageFont
import io, random, datetime, requests

TOKEN = "8407032246:AAFBcewVBGxRRv8P2XKIUaHSXYh6kxvZeiQ"

# -----------------------------
# Fun / Entertainment
# -----------------------------
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = ["Joke 1", "Joke 2"]
    await update.message.reply_text(random.choice(jokes))

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = ["Quote 1", "Quote 2"]
    await update.message.reply_text(random.choice(quotes))

async def magic8ball(update: Update, context: ContextTypes.DEFAULT_TYPE):
    responses = ["Yes", "No", "Maybe", "Definitely", "Ask again later"]
    await update.message.reply_text(random.choice(responses))

async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trivia_list = ["Trivia 1", "Trivia 2"]
    await update.message.reply_text(random.choice(trivia_list))

# -----------------------------
# Creative / Media
# -----------------------------
async def avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /avatar YourName")
        return
    name = " ".join(context.args)
    img = Image.new("RGB", (400, 400), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    w, h = draw.textsize(name, font=font)
    draw.text(((400-w)/2,(400-h)/2), name, font=font, fill=(255,255,255))
    bio = io.BytesIO()
    bio.name = "avatar.png"
    img.save(bio, "PNG")
    bio.seek(0)
    await update.message.reply_photo(photo=bio, caption=f"Avatar for {name}")

async def banner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /banner YourText")
        return
    text = " ".join(context.args)
    img = Image.new("RGB", (600, 150), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    w, h = draw.textsize(text, font=font)
    draw.text(((600-w)/2,(150-h)/2), text, font=font, fill=(255,255,255))
    bio = io.BytesIO()
    bio.name = "banner.png"
    img.save(bio, "PNG")
    bio.seek(0)
    await update.message.reply_photo(photo=bio, caption=f"Banner: {text}")

async def emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /emoji 😄 🚀")
        return
    await update.message.reply_text("".join(context.args))

async def photo_to_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Send a photo to get a URL!")
        return
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "temp.jpg"
    await file.download_to_drive(file_path)
    # Placeholder for Telegraph or other upload
    await update.message.reply_text(f"✅ Photo saved as {file_path} (you can replace with your upload logic)")

# -----------------------------
# Placeholder Image Commands
# -----------------------------
async def hwaifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💖 Placeholder: Send your own SFW hwaifu image API here.")

async def nsfw_placeholder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Placeholder: You can add your custom NSFW or private image source here.")

# -----------------------------
# Utility / Productivity
# -----------------------------
async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    await update.message.reply_text(f"Current time: {now} ⏰")

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    await update.message.reply_text(f"Today's date: {today} 📅")

async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /calc 2+2*3")
        return
    expression = "".join(context.args)
    try:
        result = eval(expression)
        await update.message.reply_text(f"{expression} = {result}")
    except:
        await update.message.reply_text("❌ Invalid expression!")

# -----------------------------
# Games
# -----------------------------
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎲 You rolled a {random.randint(1,6)}")

async def flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🪙 Coin flip: {random.choice(['Heads','Tails'])}")

async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /rps rock/paper/scissors")
        return
    user_choice = context.args[0].lower()
    choices = ["rock","paper","scissors"]
    bot_choice = random.choice(choices)
    result = "Draw"
    if (user_choice=="rock" and bot_choice=="scissors") or \
       (user_choice=="paper" and bot_choice=="rock") or \
       (user_choice=="scissors" and bot_choice=="paper"):
        result = "You win! 🎉"
    elif user_choice in choices:
        result = "You lose! 😢"
    await update.message.reply_text(f"You: {user_choice}\nBot: {bot_choice}\nResult: {result}")

# -----------------------------
# Info / Links
# -----------------------------
async def website(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 Website: https://waikwa.vercel.app")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 Contact:\nPhone: +254715155196\nInstagram: @cytra_k9\nEmail: jackwaikwa1@gmail.com"
    )

async def products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📦 Products:\nProduct A - $49\nProduct B - $79\nProduct C - $120"
    )

async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ FAQs:\nQ: Working hours?\nA: 9 AM - 6 PM\nQ: Delivery? Yes, 3-5 business days."
    )

# -----------------------------
# Menu / Inline Keyboard
# -----------------------------
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Games", callback_data="games")],
        [InlineKeyboardButton("🎨 Creative", callback_data="creative")],
        [InlineKeyboardButton("🛠 Utility", callback_data="utility")],
        [InlineKeyboardButton("📄 Info", callback_data="info")],
        [InlineKeyboardButton("😂 Fun", callback_data="fun")],
        [InlineKeyboardButton("💖 Hwaifu Placeholder", callback_data="hwaifu")],
        [InlineKeyboardButton("⚠️ NSFW Placeholder", callback_data="nsfw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📜 Select a category:", reply_markup=reply_markup)

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    text = ""
    if data == "games":
        text = "🎲 Games:\n/roll\n/flip\n/rps"
    elif data == "creative":
        text = "🎨 Creative:\n/avatar\n/banner\n/emoji\nSend a photo for URL"
    elif data == "utility":
        text = "🛠 Utility:\n/time\n/date\n/calc"
    elif data == "info":
        text = "📄 Info:\n/website\n/contact\n/products\n/faq"
    elif data == "fun":
        text = "😂 Fun:\n/joke\n/quote\n/8ball\n/trivia"
    elif data == "hwaifu":
    text = "https://api.waifu.pics/nsfw/neko"
    elif data == "nsfw":
        text = "https://api.waifu.pics/nsfw/blowjob"
    await query.edit_message_text(text=text)

# -----------------------------
# Start
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Use /menu to see all command categories.")

# -----------------------------
# Main
# -----------------------------
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Fun
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("8ball", magic8ball))
    app.add_handler(CommandHandler("trivia", trivia))
    
    # Creative
    app.add_handler(CommandHandler("avatar", avatar))
    app.add_handler(CommandHandler("banner", banner))
    app.add_handler(CommandHandler("emoji", emoji))
    app.add_handler(MessageHandler(filters.PHOTO, photo_to_url))
    
    # Placeholders
    app.add_handler(CommandHandler("hwaifu", hwaifu))
    app.add_handler(CommandHandler("nsfw_placeholder", nsfw_placeholder))
    
    # Utility
    app.add_handler(CommandHandler("time", time))
    app.add_handler(CommandHandler("date", date))
    app.add_handler(CommandHandler("calc", calc))
    
    # Games
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("flip", flip))
    app.add_handler(CommandHandler("rps", rps))
    
    # Info
    app.add_handler(CommandHandler("website", website))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("products", products))
    app.add_handler(CommandHandler("faq", faq))
    
    # Menu
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(menu_callback))
    
    # Start
    app.add_handler(CommandHandler("start", start))
    
    print("🤖 SuperBot with placeholders is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
