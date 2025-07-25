import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID =  os.getenv('CHANNEL_ID')

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
)
dp = Dispatcher()

async def wait_for_next_minute():
    """Ждём, пока секунды не станут 0"""
    ekb_tz = pytz.timezone('Asia/Yekaterinburg')
    while True:
        now = datetime.now(ekb_tz)
        if now.second == 0:
            return
        await asyncio.sleep(0.5)

async def update_time_message():
    ekb_tz = pytz.timezone('Asia/Yekaterinburg') 
    message_id = 48
    await wait_for_next_minute()
    while True:
        now = datetime.now(ekb_tz)

        day = now.strftime('%d')
        month = now.strftime('%m')
        year = now.year
        dayOfWeek = now.strftime('%A')
        hour = now.strftime('%H')
        minute = now.strftime('%M')
        seconds = now.strftime('%S')


        start_of_year = datetime(year=year, month=1, day=1, tzinfo=ekb_tz)
        end_of_year = datetime(year=year, month=12, day=31, hour=23, minute=59, second=59, tzinfo=ekb_tz)


        year_duration = (end_of_year - start_of_year).total_seconds()
        year_passed = (now - start_of_year).total_seconds()
        year_progress = (year_passed / year_duration) * 100

        day_seconds = now.hour * 3600 + now.minute * 60 + now.second
        day_progress = (day_seconds / 86400) * 100

        text = (
            f"```javascript\n"
            f"const life = {{\n"
            f"  day: {day},\n"
            f"  month: {month},\n"
            f"  year: {year},\n"
            f"  dayOfWeek: '{dayOfWeek}',\n"
            f"  hour: {hour},\n"
            f"  minute: {minute},\n"
            f"  seconds: {seconds},\n"
            f"  dayProgress: {day_progress:.2f}%,\n"
            f"  yearProgress: {year_progress:.6f}%,\n"
            f"}}\n"
            f"```"
        )

        try:
            if message_id is None:
                msg = await bot.send_message(CHANNEL_ID, text)
                message_id = msg.message_id
            else:
                await bot.edit_message_text(text, chat_id=CHANNEL_ID, message_id=message_id)
        except Exception as e:
            print(f'Ошибка: {e}')

        await asyncio.sleep(10)

async def main():
    asyncio.create_task(update_time_message())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
