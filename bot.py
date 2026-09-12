import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Config Credentials
TOKEN = "8754613225:AAGhf0tpxlSSYQoMw2Twi7qwa6fxsDtApSI"
ADMIN_ID = 6516107821

# Web App URL (Corrected GitHub Pages Link)
WEB_APP_URL = "https://mdrabbihosin062-wq.github.io/my-telegram-bot/"

# VIP Links (Sent after Admin Approval)
VIP_LINKS = """
🎉 **আপনার পেমেন্ট ভেরিফাই হয়েছে! VIP এক্সেস আনলকড:**

🔗 [VIP Channel 1](https://t.me/example1)
🔗 [VIP Channel 2](https://t.me/example2)
🔗 [VIP Channel 3](https://t.me/example3)
🔗 [VIP Channel 4](https://t.me/example4)
🔗 [VIP Channel 5](https://t.me/example5)
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ভিডিও দেখতে অ্যাপ খুলুন 🔞", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 **স্বাগতম VIP সার্ভিস এ!**\n\nপেমেন্ট সম্পন্ন করতে নিচের বাটনে চাপ দিন:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.message.web_app_data.data)
    user = update.effective_user
    
    phone = data.get("phone", "N/A")
    trx_id = data.get("trxId", "N/A")
    method = data.get("method", "bKash/Nagad")

    # Reply to User
    await update.message.reply_text(
        "✅ **আপনার পেমেন্ট তথ্য জমা নেওয়া হয়েছে!**\nএডমিন ভেরিফাই করে শীঘ্রই আপনাকে এক্সেস দেবেন।",
        parse_mode="Markdown"
    )

    # Notify Admin with Approve Button
    admin_keyboard = [
        [InlineKeyboardButton("✅ Approve / Accept", callback_data=f"approve_{user.id}")]
    ]
    admin_markup = InlineKeyboardMarkup(admin_keyboard)

    admin_msg = (
        f"📥 **নতুন পেমেন্ট রিকোয়েস্ট!**\n\n"
        f"👤 **ইউজার:** {user.full_name} (@{user.username})\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"💳 **মেথড:** {method}\n"
        f"📞 **ফোন:** `{phone}`\n"
        f"🧾 **TrxID:** `{trx_id}`"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_msg,
        reply_markup=admin_markup,
        parse_mode="Markdown"
    )

async def admin_approval_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data
    if data.startswith("approve_"):
        user_id = int(data.split("_")[1])
        
        # Send Links to User
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=VIP_LINKS,
                parse_mode="Markdown"
            )
            await query.edit_message_text(text=f"{query.message.text}\n\n✅ **Approved & VIP Links Sent!**")
        except Exception as e:
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **Failed to send message: {e}**")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    app.add_handler(CallbackQueryHandler(admin_approval_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
