import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# فعال سازی لاگینگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# دریافت توکن ربات و ID ادمین از متغیرهای محیطی
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID:
    ADMIN_ID = int(ADMIN_ID)
else:
    logger.error("ADMIN_ID environment variable not set!")
    exit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info = "🆕 New user started the bot:\n"
    info += f"👤 Name: {user.full_name}\n"
    info += f"🆔 ID: {user.id}\n"
    if user.username:
        info += f"🔗 Username: @{user.username}\n"
    info += f"🌐 Language: {user.language_code or 'unknown'}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=info)
    logger.info(f"User {user.id} started the bot.")

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"New message from user {user.id}: {update.message.text if update.message.text else '<media>'}")

    info = "📩 New message from user:\n"
    info += f"👤 Name: {user.full_name}\n"
    info += f"🆔 ID: {user.id}\n"
    if user.username:
        info += f"🔗 Username: @{user.username}"

    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=info)
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"⚠️ Error forwarding message from {user.id}: {e}")
        logger.error(f"Error forwarding message from user {user.id}: {e}")

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not update.message.reply_to_message or not hasattr(update.message.reply_to_message, 'forward_from'):
        return

    target_user_id = update.message.reply_to_message.forward_from.id
    msg = update.message

    logger.info(f"Admin {ADMIN_ID} is replying to user {target_user_id}.")

    try:
        if msg.text:
            await context.bot.send_message(chat_id=target_user_id, text=msg.text)
            logger.info(f"Reply sent to user {target_user_id}: {msg.text}")
        elif msg.photo:
            await context.bot.send_photo(chat_id=target_user_id, photo=msg.photo[-1].file_id, caption=msg.caption)
            logger.info(f"Photo reply sent to user {target_user_id}.")
        elif msg.video:
            await context.bot.send_video(chat_id=target_user_id, video=msg.video.file_id, caption=msg.caption)
            logger.info(f"Video reply sent to user {target_user_id}.")
        elif msg.document:
            await context.bot.send_document(chat_id=target_user_id, document=msg.document.file_id, caption=msg.caption)
            logger.info(f"Document reply sent to user {target_user_id}.")
        elif msg.voice:
            await context.bot.send_voice(chat_id=target_user_id, voice=msg.voice.file_id, caption=msg.caption)
            logger.info(f"Voice reply sent to user {target_user_id}.")
        elif msg.audio:
            await context.bot.send_audio(chat_id=target_user_id, audio=msg.audio.file_id, caption=msg.caption)
            logger.info(f"Audio reply sent to user {target_user_id}.")
        elif msg.sticker:
            await context.bot.send_sticker(chat_id=target_user_id, sticker=msg.sticker.file_id)
            logger.info(f"Sticker reply sent to user {target_user_id}.")
    except Exception as e:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Error sending reply to {target_user_id}: {e}")
        logger.error(f"Error sending reply to user {target_user_id}: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a telegram message to notify the developer."""
    logger.error(f"Exception while handling an update {update}:", exc_info=context.error)

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN environment variable not set!")
        exit()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & filters.REPLY, handle_reply))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))
    app.add_error_handler(error_handler)

    logger.info("🤖 Bot is starting...")
    app.run_polling()
