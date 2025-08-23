import os
import tempfile
from openai import OpenAI
from pydub import AudioSegment
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ---------------------------
# Environment variables
# ---------------------------
OPENAI_API_KEY = os.environ.get("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")
TELEGRAM_TOKEN = os.environ.get("8407032246:AAFBcewVBGxRRv8P2XKIUaHSXYh6kxvZeiQ")

client = OpenAI(api_key=OPENAI_API_KEY)

USER_MEMORY = {}
MAX_MEMORY_MESSAGES = 10

def add_to_memory(user_id: int, role: str, content: str):
    hist = USER_MEMORY.setdefault(user_id, [])
    hist.append({"role": role, "content": content})
    if len(hist) > MAX_MEMORY_MESSAGES:
        USER_MEMORY[user_id] = hist[-MAX_MEMORY_MESSAGES:]

def build_messages_for_user(user_id: int, user_prompt: str):
    system = {"role": "system", "content": "You are a helpful Telegram chatbot. Reply politely in English/Swahili."}
    history = USER_MEMORY.get(user_id, [])
    return [system] + history + [{"role": "user", "content": user_prompt}]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Habari! Mimi ni bot yako 🤖\n"
        "- Send text messages\n"
        "- Send voice notes (transcribed)\n"
        "- /image <prompt> to generate images\n"
        "- /clearmemory to clear history"
    )

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_MEMORY.pop(update.effective_user.id, None)
    await update.message.reply_text("Memory cleared ✅")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    add_to_memory(user_id, "user", user_text)
    messages = build_messages_for_user(user_id, user_text)

    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        reply = resp.choices[0].message.content.strip()
    except Exception as e:
        reply = f"OpenAI error: {e}"

    add_to_memory(user_id, "assistant", reply)
    await update.message.reply_text(reply)

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user_id = update.effective_user.id
    voice = message.voice
    if not voice:
        await update.message.reply_text("No voice note received.")
        return

    file = await voice.get_file()
    with tempfile.TemporaryDirectory() as tmpdir:
        ogg_path = os.path.join(tmpdir, "voice.ogg")
        mp3_path = os.path.join(tmpdir, "voice.mp3")
        await file.download_to_drive(ogg_path)

        try:
            audio = AudioSegment.from_file(ogg_path)
            audio.export(mp3_path, format="mp3")
        except Exception as e:
            await update.message.reply_text(f"Conversion error: {e}")
            return

        try:
            with open(mp3_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                text = transcript.text
        except Exception as e:
            await update.message.reply_text(f"Transcription error: {e}")
            return

    add_to_memory(user_id, "user", text)
    messages = build_messages_for_user(user_id, text)
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = resp.choices[0].message.content.strip()
    except Exception as e:
        reply = f"OpenAI error: {e}"

    add_to_memory(user_id, "assistant", reply)
    await update.message.reply_text(f"Transcription:\n{text}\n\nReply:\n{reply}")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /image <description>")
        return
    prompt = " ".join(context.args)
    await update.message.reply_text("Generating image... ✨")
    try:
        img_resp = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="512x512"
        )
        img_url = img_resp.data[0].url
        await update.message.reply_photo(img_url, caption=f"Image for: {prompt}")
    except Exception as e:
        await update.message.reply_text(f"Image generation error: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clearmemory", clear_memory))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
