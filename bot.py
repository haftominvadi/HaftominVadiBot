import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# وقتی کاربر استارت می‌زند
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info = "🆕 New user started the bot:\n"
    info += f"👤 Name: {user.full_name}\n"
    info += f"🆔 ID: {user.id}\n"
    if user.username:
        info += f"🔗 Username: @{user.username}\n"
    info += f"🌐 Language: {user.language_code or 'unknown'}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=info)

# فوروارد کردن پیام کاربر + ارسال اطلاعات کاربر
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    info = "📩 New message from user:\n"
    info += f"👤 Name: {user.full_name}\n"
    info += f"🆔 ID: {user.id}\n"
    if user.username:
        info += f"🔗 Username: @{user.username}"

    try:
        # ابتدا اطلاعات کاربر را بفرست
        await context.bot.send_message(chat_id=ADMIN_ID, text=info)
        # سپس پیام را فوروارد کن
        await context.bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"⚠️ Error forwarding message: {e}")

# پاسخ ادمین به پیام فوروارد شده
async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not update.message.reply_to_message or not update.message.reply_to_message.forward_from:
        return

    target_user_id = update.message.reply_to_message.forward_from.id
    msg = update.message

    try:
        if msg.text:
            await context.bot.send_message(chat_id=target_user_id, text=msg.text)
        elif msg.photo:
            await context.bot.send_photo(chat_id=target_user_id, photo=msg.photo[-1].file_id, caption=msg.caption)
        elif msg.video:
            await context.bot.send_video(chat_id=target_user_id, video=msg.video.file_id, caption=msg.caption)
        elif msg.document:
            await context.bot.send_document(chat_id=target_user_id, document=msg.document.file_id, caption=msg.caption)
        elif msg.voice:
            await context.bot.send_voice(chat_id=target_user_id, voice=msg.voice.file_id, caption=msg.caption)
        elif msg.audio:
            await context.bot.send_audio(chat_id=target_user_id, audio=msg.audio.file_id, caption=msg.caption)
        elif msg.sticker:
            await context.bot.send_sticker(chat_id=target_user_id, sticker=msg.sticker.file_id)
    except Exception as e:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Error sending reply: {e}")

# اجرای اصلی
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL & filters.REPLY, handle_reply))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))

    print("🤖 Bot is running...")
    app.run_polling()