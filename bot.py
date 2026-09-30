import os
import json
import re
from difflib import SequenceMatcher

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN")

# Search requests should only be answered in this group
SEARCH_GROUP = "@annamoviereq"


def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def load_movies():
    try:
        with open("movies.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("movies.json load error:", e)
        return []


MOVIES = load_movies()

print(f"Loaded {len(MOVIES)} movie records")


def similarity(query, text):
    query = normalize(query)
    text = normalize(text)

    if query == text:
        return 100

    if query in text:
        return 90

    return int(SequenceMatcher(None, query, text).ratio() * 100)


def search_movies(query):
    query = normalize(query)

    results = []

    for movie in MOVIES:
        title = movie.get("title", "")
        search_text = movie.get("search_text", "")

        title_score = similarity(query, title)
        text_score = similarity(query, search_text)

        score = max(title_score, text_score)

        if query in normalize(search_text):
            score = max(score, 85)

        if score >= 45:
            results.append((score, movie))

    results.sort(key=lambda x: x[0], reverse=True)

    return results[:5]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Anna's Movie Search Bot\n\n"
        "🔎 ဇာတ်ကားနာမည်ကို Group ထဲမှာ ရိုက်ထည့်ပြီး ရှာနိုင်ပါတယ်။"
    )


async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat = update.effective_chat

    # Ignore private chats and other groups
    if chat.username and chat.username.lower() != SEARCH_GROUP.replace("@", "").lower():
        return

    query = update.message.text.strip()

    # Ignore commands and very short messages
    if query.startswith("/") or len(query) < 2:
        return

    results = search_movies(query)

    if not results:
        await update.message.reply_text(
            f"😔 '{query}' ကို မတွေ့သေးပါဘူး။\n\n"
            "🔎 ဇာတ်ကားနာမည်ကို English လို ပြန်စမ်းရှာကြည့်ပါ။"
        )
        return

    for score, movie in results:
        title = movie.get("title", "Movie")
        links = movie.get("links", [])

        if not links:
            continue

        # Avoid creating too many buttons
        buttons = []

        for i, link in enumerate(links[:10], start=1):
            if len(links) == 1:
                label = "🎬 ဇာတ်ကားကြည့်ရန်"
            else:
                label = f"▶️ Part / EP {i}"

            buttons.append(
                [InlineKeyboardButton(label, url=link)]
            )

        keyboard = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(
            f"🎬 {title}\n"
            f"🔎 Match: {score}%",
            reply_markup=keyboard,
            disable_web_page_preview=True,
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

    print("Anna Movie Search Bot is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
