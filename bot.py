from telegram import Update, ChatPermissions
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from datetime import timedelta
import re

TOKEN = "8686888169:AAGGcey6MowZ5HVKQ7pdv0rVX9M0njJsq_s"

# 🧠 دیتابیس ساده داخل حافظه
warns = {}
levels = {}
last_message_time = {}

# 🚫 فحش‌ها (قابل توسعه)
BAD_WORDS = ["کص", "کیر", "ننت", "مادرت", "عمه", "خاله", "سیکتیر"]

# 🚫 لینک‌ها
LINK_PATTERN = r"(https?://|t\.me/|www\.)"

def clean(text):
    return text.replace(".", "").replace(" ", "").lower()

# 👋 ورود
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(f"👋 خوش آمدی {user.first_name} عزیز!")
    await update.message.delete()

# 🚪 خروج
async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😢 یه نفر رفت از گروه...")

# 🚨 مدیریت پیام‌ها
async def moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text_raw = update.message.text
    text = clean(text_raw)
    user = update.message.from_user
    user_id = user.id
    chat_id = update.effective_chat.id

    # 💬 سلام
    if text == "سلام":
        await update.message.reply_text("سلام 🖐️")
        return

    # ⛔ لینک
    if re.search(LINK_PATTERN, text_raw):
        await update.message.reply_text("🚫 ارسال لینک ممنوع است!")
        return

    # 🚫 فحش
    for bad in BAD_WORDS:
        if bad in text:
            warns[user_id] = warns.get(user_id, 0) + 1

            await update.message.reply_text(f"⚠️ اخطار {warns[user_id]}")

            # 3 اخطار = میوت
            if warns[user_id] >= 3:
                await update.message.reply_text("🚫 3 اخطار → میوت 1 ساعت")

                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=update.message.date + timedelta(hours=1)
                )
                warns[user_id] = 0
            return

    # 🧠 Level system
    levels[user_id] = levels.get(user_id, 0) + 1

    # 🏆 پیام level
    if levels[user_id] % 10 == 0:
        await update.message.reply_text(f"🏆 تبریک! لول تو شد {levels[user_id]}")

    # 🚀 ضد اسپم ساده
    import time
    now = time.time()

    if user_id in last_message_time:
        if now - last_message_time[user_id] < 2:
            await update.message.reply_text("⛔ اسپم نکن!")
            return

    last_message_time[user_id] = now

# 🚀 اجرا
app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderation))

print("🔥 SUPER PRO Group Bot Running...")
app.run_polling()