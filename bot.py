import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

BOT_TOKEN = "8754613225:AAGhf0tpxlSSYQoMw2Twi7qwa6fxsDtApSI" 
ADMIN_ID = 6516107821 
WEB_APP_URL = "https://chipper-dieffenbachia-389115.netlify.app/" 

VIP_LINKS = (
    "🔞 **VIP PREMIUM CHANNELS** 🔞\n\n"
    "1️⃣ Link: https://t.me/+pMTawaS6bVkyOTE1\n"
    "2️⃣ Link: https://t.me/+ZduWN4W0O4BmODk1\n"
    "3️⃣ Link: https://t.me/+MfTT85MiuKMwYTg9\n"
    "4️⃣ Link: https://t.me/+JLSVi33prEZhMzI1\n"
    "5️⃣ Link: https://t.me/+wW54kBh0AM42MzBl"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ভিডিও দেখতে অ্যাপ খুলুন 🔞", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "স্বাগতম! নিচের বাটনে ক্লিক করে পেমেন্ট সম্পন্ন করে প্রিমিয়াম কন্টেন্ট আনলক করুন:", 
        reply_markup=reply_markup
    )

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.message.web_app_data.data)
    user = update.message.from_user
    
    msg = (
        f"🔔 **নতুন পেমেন্ট রিকোয়েস্ট!**\n\n"
        f"👤 ইউজার: @{user.username} (ID: `{user.id}`)\n"
        f"📞 বিকাশ/নগদ নম্বর: `{data['phone']}`\n"
        f"💳 TrxID: `{data['trxId']}`"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Accept (Approve)", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
        ]
    ]
    
    await context.bot.send_message(
        chat_id=ADMIN_ID, 
        text=msg, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )
    
    await update.message.reply_text(
        "আপনার পেমেন্ট রিকোয়েস্ট এডমিনের কাছে জমা হয়েছে! ট্রানজেকশন আইডি চেক করে এপ্রুভ করলেই প্রাইভেট লিংক পেয়ে যাবেন।"
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("_")
    action = data[0]
    target_user_id = int(data[1])
    
    if action == "approve":
        await context.bot.send_message(
            chat_id=target_user_id, 
            text=f"🎉 আপনার পেমেন্ট সফল হয়েছে! আপনার এক্সেস লিংকসমূহ নিচে দেওয়া হলো:\n\n{VIP_LINKS}"
        )
        await query.edit_message_text(text=query.message.text + "\n\n✅ **Status: Approved!**")
        
    elif action == "reject":
        await context.bot.send_message(
            chat_id=target_user_id, 
            text="❌ আপনার ট্রানজেকশন আইডিটি সঠিক পাওয়া যায়নি। অনুগ্রহ করে সঠিক তথ্য দিয়ে পুনরায় চেষ্টা করুন।"
        )
        await query.edit_message_text(text=query.message.text + "\n\n❌ **Status: Rejected!**")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is running...")
    app.run_polling()

