import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

# چت‌آیدی کاربران ذخیره می‌شود تا بتوان به پیام‌های فوروارد شده پاسخ داد
forwarded_messages = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# وقتی کاربر استارت می‌زند
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    info = f"🚀 New user started the bot:\n"
    info += f"👤 Name: {user.full_name}\n"
    info += f"🆔 ID: {user.id}\n"
    if user.username:
        info += f"🔗 Username: @{user.username}\n"

    await context.bot.send_message(chat_id=ADMIN_ID, text=info)

# فوروارد واقعی پیام و ثبت شناسه پیام فورواردی برای پاسخ‌دهی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    info = f"👤 {user.full_name} ({user.id})"
    if user.username:
        info += f"\n🔗 Username: @{user.username}"

    # فوروارد واقعی پیام کاربر
    forwarded = await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.effective_chat.id,
        message_id=message.message_id
    )

    # ذخیره کردن ارتباط بین پیام فورواردی و چت کاربر
    forwarded_messages[forwarded.message_id] = update.effective_chat.id

    # ارسال اطلاعات کاربر بالای پیام
    await context.bot.send_message(chat_id=ADMIN_ID, text=info)

# ادمین با ریپلای به پیام فوروارد شده، پاسخ را به کاربر ارسال می‌کند
async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        return

    original_msg_id = update.message.reply_to_message.message_id
    user_chat_id = forwarded_messages.get(original_msg_id)

    if not user_chat_id:
        await update.message.reply_text("⚠️ No user mapped to this forwarded message.")
        return

    # ارسال پاسخ به کاربر
    if update.message.text:
        await context.bot.send_message(chat_id=user_chat_id, text=update.message.text)
    elif update.message.photo:
        await context.bot.send_photo(chat_id=user_chat_id, photo=update.message.photo[-1].file_id, caption=update.message.caption)
    elif update.message.video:
        await context.bot.send_video(chat_id=user_chat_id, video=update.message.video.file_id, caption=update.message.caption)
    elif update.message.document:
        await context.bot.send_document(chat_id=user_chat_id, document=update.message.document.file_id, caption=update.message.caption)
    elif update.message.voice:
        await context.bot.send_voice(chat_id=user_chat_id, voice=update.message.voice.file_id, caption=update.message.caption)
    elif update.message.sticker:
        await context.bot.send_sticker(chat_id=user_chat_id, sticker=update.message.sticker.file_id)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.REPLY & filters.ALL, handle_reply))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()
