import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS

# 🔑 Replace these with your real keys
TELEGRAM_TOKEN = "8407032246:AAFBcewVBGxRRv8P2XKIUaHSXYh6kxvZeiQ"
GEMINI_API_KEY = "AIzaSyAN_S9y9C2xi_lYhJz41-uItJedpcDU4_4"

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- User state ---
user_modes = {}
user_langs = {}
user_contexts = {}

# --- Gemini Chat API ---
def ask_gemini(prompt: str, mode: str = "default") -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/chat-bison-001:generateMessage"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    # Add mode instructions
    if mode == "creative":
        prompt = f"Be very imaginative and creative: {prompt}"
    elif mode == "code":
        prompt = f"Answer with clean, well-formatted code only: {prompt}"
    elif mode == "short":
        prompt = f"Answer very briefly: {prompt}"

    data = {
        "messages": [
            {"author": "user", "content": {"text": prompt}}
        ]
    }

    response = requests.post(url, headers=headers, params=params, json=data)
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"][0]["text"]
    else:
        return f"Error: {response.text}"

# --- Gemini Image API ---
def create_image(prompt: str):
    url = "https://generativelanguage.googleapis.com/v1beta/models/image-bison-001:generate"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {"prompt": {"text": prompt}}

    response = requests.post(url, headers=headers, params=params, json=data)
    if response.status_code == 200:
        img_base64 = response.json()["images"][0]["image"]
        return img_base64
    return None

# --- TTS ---
def text_to_speech(text: str, lang: str = "en", filename: str = "reply.mp3"):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_modes[user_id] = "default"
    user_langs[user_id] = "en"
    user_contexts[user_id] = []

    await update.message.reply_text(
        "👋 Hi, I'm your Gemini bot! 😁\n\n"
        "Developed by **Cytra** 🔹 Visit: [waikwa.vercel.app](https://waikwa.vercel.app)\n\n"
        "✨ Features:\n"
        "- `/mode <default|creative|code|short>` → set reply style\n"
        "- `/reset` → clear conversation\n"
        "- `/image <prompt>` → generate an image\n"
        "- `/lang <code>` → set TTS language (en, hi, es, ar, ja...)\n"
        "- `/speak <text>` → make me talk\n\n"
        "Just type any message to start chatting!"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_contexts[user_id] = []
    await update.message.reply_text("✅ Conversation reset!")

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.args:
        mode = context.args[0].lower()
        if mode in ["default", "creative", "code", "short"]:
            user_modes[user_id] = mode
            await update.message.reply_text(f"✅ Mode set to *{mode}*.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Available modes: default, creative, code, short")
    else:
        await update.message.reply_text("Usage: /mode <default|creative|code|short>")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /image <your prompt>")
        return

    prompt = " ".join(context.args)
    await update.message.reply_text(f"🎨 Creating image: {prompt}")

    image_base64 = create_image(prompt)
    if image_base64:
        await update.message.reply_photo(photo=bytes(image_base64, "utf-8"))
    else:
        await update.message.reply_text("❌ Failed to generate image.")

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args:
        await update.message.reply_text(
            "Usage: /lang <code>\nExamples: en (English), hi (Hindi), es (Spanish), ar (Arabic), ja (Japanese)"
        )
        return
    lang_code = context.args[0].lower()
    try:
        gTTS("test", lang=lang_code)
        user_langs[user_id] = lang_code
        await update.message.reply_text(f"✅ Language set to {lang_code}")
    except:
        await update.message.reply_text("❌ Unsupported language code.")

async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    lang = user_langs.get(user_id, "en")
    if not context.args:
        await update.message.reply_text("Usage: /speak <text>")
        return
    text = " ".join(context.args)
    filename = text_to_speech(text, lang)
    await update.message.reply_voice(voice=open(filename, "rb"))

# --- Handle normal messages ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    mode = user_modes.get(user_id, "default")
    lang = user_langs.get(user_id, "en")

    await update.message.reply_text("🤔 Thinking...")
    reply = ask_gemini(text, mode)
    await update.message.reply_text(reply)

    # auto voice reply
    filename = text_to_speech(reply, lang)
    await update.message.reply_voice(voice=open(filename, "rb"))

# --- Main ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("mode", set_mode))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(CommandHandler("lang", set_lang))
    app.add_handler(CommandHandler("speak", speak))

    # Text message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Gemini Ultimate Bot running on Termux! Developed by Cytra 😁")
    app.run_polling()

if __name__ == "__main__":
    main()
