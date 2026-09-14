import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Logging Configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Configuration ---
TOKEN = "8754613225:AAGhf0tpxlSSYQoMw2Twi7qwa6fxsDtApSI"
ADMIN_ID = 6516107821

# আপনার নতুন প্রাইভেট VIP চ্যানেলের ইনভাইট লিংক
VIP_CHANNEL_LINK = "https://t.me/+ZduWN4W0O4BmODk1"

PREVIEW_TEXT = """
🔞 **VIP Premium Membership Access**

ভিডিও টিজার দেখে সম্পূর্ণ অ্যাক্সেস পেতে সাবস্ক্রাইব করুন!

💰 **ফি:** ৳৫০০ (১ মাস)
💳 **bKash / Nagad (Personal):** `01859620810`

পেমেন্ট করার পর নিচের **"💳 পেমেন্ট নিশ্চিত করুন"** বাটনে চাপ দিয়ে আপনার ফোন নম্বর ও TrxID জমা দিন।
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 পেমেন্ট নিশ্চিত করুন", callback_data="submit_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        PREVIEW_TEXT,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "submit_payment":
        context.user_data['awaiting_payment'] = True
        await query.message.reply_text(
            "📝 **পেমেন্ট ভেরিফিকেশন:**\n\nদয়া করে আপনার **বিকাশ/নগদ নম্বর** এবং **TrxID** একই মেসেজে লিখে পাঠান।\n\n*উদাহরণ:* `01800000000 TrxID: 9J87XX65`",
            parse_mode="Markdown"
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if context.user_data.get('awaiting_payment'):
        context.user_data['awaiting_payment'] = False
        
        await update.message.reply_text(
            "✅ **আপনার পেমেন্ট তথ্য জমা নেওয়া হয়েছে!**\nএডমিন ভেরিফাই করে আপনাকে শীঘ্রই VIP চ্যানেলের লিংক দেবেন।"
        )

        admin_keyboard = [
            [InlineKeyboardButton("✅ Approve (এক্সেস দিন)", callback_data=f"approve_{user.id}")]
        ]
        admin_markup = InlineKeyboardMarkup(admin_keyboard)

        admin_msg = (
            f"📥 **নতুন VIP পেমেন্ট রিকোয়েস্ট!**\n\n"
            f"👤 **ইউজার:** {user.full_name} (@{user.username})\n"
            f"🆔 **ID:** `{user.id}`\n\n"
            f"📩 **পেমেন্ট তথ্য:**\n{text}"
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
        
        try:
            vip_msg = (
                f"🎉 **আপনার পেমেন্ট ভেরিফাই করা হয়েছে!**\n\n"
                f"নিচের লিংকে ক্লিক করে আমাদের VIP চ্যানেলে জয়েন করুন:\n"
                f"🔗 {VIP_CHANNEL_LINK}\n\n"
                f"*নোট: ভিডিও ফরওয়ার্ড বা সেভ করা যাবে না।*"
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=vip_msg,
                parse_mode="Markdown"
            )
            await query.edit_message_text(text=f"{query.message.text}\n\n✅ **Approved! User received VIP link.**")
        except Exception as e:
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **Failed to send link: {e}**")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^submit_payment$"))
    app.add_handler(CallbackQueryHandler(admin_approval_handler, pattern="^approve_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
