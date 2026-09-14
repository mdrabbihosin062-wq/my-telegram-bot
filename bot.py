import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Logging Configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Configuration ---
TOKEN = "8754613225:AAGhf0tpxlSSYQoMw2Twi7qwa6fxsDtApSI"
ADMIN_ID = 6516107821

# VIP প্রাইভেট চ্যানেলের লিংকসমূহ
VIP_2_LINKS = """
🔗 **VIP Channel 1:** https://t.me/+pMTawaS6bVkyOTE1
🔗 **VIP Channel 2:** https://t.me/+ZduWN4W0O4BmODk1
"""

VIP_5_LINKS = """
🔗 **VIP Channel 1:** https://t.me/+pMTawaS6bVkyOTE1
🔗 **VIP Channel 2:** https://t.me/+ZduWN4W0O4BmODk1
🔗 **VIP Channel 3:** https://t.me/+MfTT85MiuKMwYTg9
🔗 **VIP Channel 4:** https://t.me/+JLSVi33prEZhMzI1
🔗 **VIP Channel 5:** https://t.me/+wW54kBh0AM42MzBl
"""

PREVIEW_TEXT = """
🔞 **VIP Premium Membership Access**

আমাদের অফারসমূহ:
🔹 **২০০ টাকা (১ মাস):** ২টি VIP চ্যানেল অ্যাক্সেস
🔹 **৫০০ টাকা (১ মাস):** ৫টি VIP চ্যানেল অ্যাক্সেস

💳 **bKash / Nagad (Personal):** `01859620810`

টাকা পাঠানোর পর নিচের **"💳 পেমেন্ট নিশ্চিত করুন"** বাটনে চাপ দিন।
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💳 পেমেন্ট নিশ্চিত করুন", callback_data="start_payment")]
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

    if query.data == "start_payment":
        keyboard = [
            [InlineKeyboardButton("📦 ৳২০০ প্যাকেজ (২ চ্যানেল)", callback_data="pkg_200")],
            [InlineKeyboardButton("📦 ৳৫০০ প্যাকেজ (৫ চ্যানেল)", callback_data="pkg_500")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "আপনার কাঙ্ক্ষিত প্যাকেজটি নির্বাচন করুন:",
            reply_markup=reply_markup
        )
    
    elif query.data in ["pkg_200", "pkg_500"]:
        pkg_amount = "২০০" if query.data == "pkg_200" else "৫০০"
        context.user_data['selected_pkg'] = query.data
        context.user_data['awaiting_payment'] = True
        
        await query.message.reply_text(
            f"📝 **{pkg_amount} টাকা পেমেন্ট ভেরিফিকেশন:**\n\nযে বিকাশ বা নগদ নম্বর থেকে টাকা পাঠিয়েছেন, শুধুমাত্র সেই **১১ ডিজিটের নম্বরটি** লিখে পাঠান।\n\n*উদাহরণ:* `01859620810`",
            parse_mode="Markdown"
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    if context.user_data.get('awaiting_payment'):
        pkg = context.user_data.get('selected_pkg', 'pkg_500')
        context.user_data['awaiting_payment'] = False
        
        pkg_title = "৳২০০ (২ চ্যানেল)" if pkg == "pkg_200" else "৳৫০০ (৫ চ্যানেল)"

        await update.message.reply_text(
            "✅ **আপনার পেমেন্ট নম্বরটি জমা নেওয়া হয়েছে!**\nএডমিন নম্বর মিলিয়ে ভেরিফাই করার পর আপনাকে VIP চ্যানেলগুলোর লিংক পাঠাবে।"
        )

        # এডমিনের কাছে ৩টি কন্ট্রোল বাটনসহ নোটিফিকেশন পাঠানো
        admin_keyboard = [
            [InlineKeyboardButton("✅ Approve (2 Links / ৳২০০)", callback_data=f"approve_2_{user.id}")],
            [InlineKeyboardButton("✅ Approve (5 Links / ৳৫০০)", callback_data=f"approve_5_{user.id}")],
            [InlineKeyboardButton("❌ Reject (বাতিল করুন)", callback_data=f"reject_{user.id}")]
        ]
        admin_markup = InlineKeyboardMarkup(admin_keyboard)

        admin_msg = (
            f"📥 **নতুন VIP পেমেন্ট রিকোয়েস্ট!**\n\n"
            f"👤 **ইউজার:** {user.full_name} (@{user.username})\n"
            f"🆔 **ID:** `{user.id}`\n"
            f"📦 **ইউজারের নির্বাচিত চয়েস:** {pkg_title}\n\n"
            f"📞 **পেমেন্ট নম্বর:** `{text}`"
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
        parts = data.split("_")
        link_count = parts[1] # "2" or "5"
        user_id = int(parts[2])
        
        if link_count == "2":
            links_to_send = VIP_2_LINKS
            count_text = "২টি"
        else:
            links_to_send = VIP_5_LINKS
            count_text = "৫টি"

        try:
            vip_msg = (
                f"🎉 **আপনার পেমেন্ট ভেরিফাই করা হয়েছে!**\n\n"
                f"নিচের লিংকগুলোতে ক্লিক করে আমাদের {count_text} VIP চ্যানেলে জয়েন করুন:\n"
                f"{links_to_send}\n"
                f"*নোট: ভিডিও ফরওয়ার্ড বা সেভ করা যাবে না।*"
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=vip_msg,
                parse_mode="Markdown"
            )
            await query.edit_message_text(text=f"{query.message.text}\n\n✅ **Approved! Sent {count_text} VIP links.**")
        except Exception as e:
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **Failed to send links: {e}**")

    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        try:
            reject_msg = "❌ **আপনার পেমেন্ট রিকোয়েস্টটি বাতিল করা হয়েছে!**\n\nসঠিক তথ্য অথবা সঠিক পেমেন্ট প্রদান করে আবার চেষ্টা করুন।"
            await context.bot.send_message(
                chat_id=user_id,
                text=reject_msg,
                parse_mode="Markdown"
            )
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **Request Rejected.**")
        except Exception as e:
            await query.edit_message_text(text=f"{query.message.text}\n\n❌ **Failed to reject: {e}**")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(start_payment|pkg_200|pkg_500)$"))
    app.add_handler(CallbackQueryHandler(admin_approval_handler, pattern="^(approve_|reject_)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
