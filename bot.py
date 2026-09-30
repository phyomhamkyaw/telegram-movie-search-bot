import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Movie Search Bot အလုပ်လုပ်နေပါပြီ!\n\n"
        "ရှာချင်တဲ့ ဇာတ်ကားနာမည်ကို ရိုက်ထည့်ပါ။"
    )


async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text.strip()

    await update.message.reply_text(
        f"🔎 ရှာဖွေနေသည် — {movie_name}"
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            search_movie
        )
    )

    print("Movie Search Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
