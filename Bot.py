import random
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ContextTypes,
)

TOKEN = "8514593907:AAEmirqB2N17ckONhbS544HyZ-8VA3_Hz7Q"

DAILY_MIN = 50
DAILY_MAX = 70

request_queue = []

approved_today = 0
daily_limit = random.randint(DAILY_MIN, DAILY_MAX)
last_reset = datetime.now().date()


def reset_daily():
    global approved_today, daily_limit, last_reset
    today = datetime.now().date()

    if today != last_reset:
        approved_today = 0
        daily_limit = random.randint(DAILY_MIN, DAILY_MAX)
        last_reset = today
        print(f"🔄 Reset | Limit: {daily_limit}")


async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.chat_join_request.from_user.id
    chat_id = update.chat_join_request.chat.id

    request_queue.append((chat_id, user_id))
    print(f"📥 Queue add: {user_id}")


async def worker(app):
    global approved_today

    while True:
        reset_daily()

        if request_queue and approved_today < daily_limit:
            chat_id, user_id = request_queue.pop(0)

            delay = random.randint(70, 300)  # TEST ke liye short delay
            print(f"⏳ Waiting {delay}s")

            await asyncio.sleep(delay)

            try:
                await app.bot.approve_chat_join_request(chat_id, user_id)
                approved_today += 1
                print(f"✅ Approved {user_id}")
            except Exception as e:
                print("❌ Error:", e)

        else:
            await asyncio.sleep(5)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(ChatJoinRequestHandler(handle_request))

print("🚀 Bot Started...")

app.job_queue.run_once(
    lambda context: asyncio.create_task(worker(app)),
    1
)

app.run_polling()
