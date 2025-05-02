import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

# Load bot token and admin ID from environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

# Store message ID mapping: forwarded message -> user ID
forwarded_messages = {}

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Handle /start command from users
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info = f"🚀 New user started the bot:\n"
    info += f"👤 Name: {user.full_name}\n"
    info += f"🆔 ID: {user.id}\n"
    if user.username:
        info += f"🔗 Username: @{user.username}\n"

    # Send user info to admin
    await context.bot.send_message(chat_id=ADMIN_ID, text=info)

# Forward all incoming messages and save user mapping
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    message = update.message

    # Forward the message as-is
    forwarded = await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=chat_id,
        message_id=message.message_id
    )

    # Map forwarded message ID to the user's chat ID
    forwarded_messages[forwarded.message_id] = chat_id

    # Send user info above the forwarded message
    user_info = f"👤 {user.full_name} ({user.id})"
    if user.username:
        user_info += f"\n🔗 Username: @{user.username}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=user_info)

# Allow admin to reply to forwarded messages
async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    reply_to = update.message.reply_to_message
    if not reply_to:
        return

    original_message_id = reply_to.message_id
    user_chat_id = forwarded_messages.get(original_message_id)

    if not user_chat_id:
        await update.message.reply_text("⚠️ Unable to identify the user.")
        return

    # Send reply to user in the original chat
    if update.message.text:
        await context.bot.send_message(chat_id=user_chat_id, text=update.message.text)
    elif update.message.photo:
        await context.bot.send_photo(chat_id=user_chat_id, photo=update.message.photo[-1].file_id, caption=update.message.caption)
    elif update.message.video:
        await context.bot.send_video(chat_id=user_chat_id, video=update.message.video.file_id, caption=update.message.caption)
    elif update.message.voice:
        await context.bot.send_voice(chat_id=user_chat_id, voice=update.message.voice.file_id, caption=update.message.caption)
    elif update.message.document:
        await context.bot.send_document(chat_id=user_chat_id, document=update.message.document.file_id, caption=update.message.caption)
    elif update.message.sticker:
        await context.bot.send_sticker(chat_id=user_chat_id, sticker=update.message.sticker.file_id)

# Run the bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.REPLY & filters.ALL, handle_admin_reply))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_admin))

    print("🤖 Bot is running...")
    app.run_polling()
