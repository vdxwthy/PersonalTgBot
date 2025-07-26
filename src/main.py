import asyncio
import configparser
import os
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from datetime import datetime, timedelta, timezone
import pytz
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID =  os.getenv('CHANNEL_ID')
CONFIG_FILE = 'settings.conf'

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
)
dp = Dispatcher()

async def wait_for_next_minute(tz_offset):
    """Wait until seconds become 0"""
    tz = timezone(timedelta(hours=tz_offset))
    while True:
        now = datetime.now(tz)
        if now.second == 0:
            return
        await asyncio.sleep(0.5)

def load_settings():
    config = configparser.ConfigParser()
    if Path(CONFIG_FILE).exists():
        config.read(CONFIG_FILE)
        try:
            message_id_str = config.get('Telegram', 'message_id', fallback='None')
            message_id = None if message_id_str == 'None' else int(message_id_str)
            
            field_order = config.get('Order', 'fields', fallback='year,month,days,day_of_week,hours,minutes,seconds,day_progress,year_progress').split(',')
            field_order = [field.strip() for field in field_order]
            
            return {
                'message_id': message_id,
                'year': config.getboolean('Features', 'year', fallback=True),
                'month': config.getboolean('Features', 'month', fallback=True),
                'days': config.getboolean('Features', 'days', fallback=True),
                'hours': config.getboolean('Features', 'hours', fallback=True),
                'minutes': config.getboolean('Features', 'minutes', fallback=True),
                'seconds': config.getboolean('Features', 'seconds', fallback=True),
                'day_of_week': config.getboolean('Features', 'day_of_week', fallback=True),
                'day_progress': config.getboolean('Features', 'day_progress', fallback=True),
                'year_progress': config.getboolean('Features', 'year_progress', fallback=True),
                'update_interval': config.getint('Features', 'update_interval', fallback=5),
                'timezone_offset': config.getint('Features', 'timezone_offset', fallback=5),
                'field_order': field_order,
            }
        except (KeyError, ValueError) as e:
            print(f"Error occurred while loading settings: {str(e)}")
            return {
                'message_id': None,
                'year': True,
                'month': True,
                'days': True,
                'hours': True,
                'minutes': True,
                'seconds': True,
                'day_of_week': True,
                'day_progress': True,
                'year_progress': True,
                'update_interval': 5,
                'timezone_offset': 5,
                'field_order': ['year','month','days','day_of_week','hours','minutes','seconds','day_progress','year_progress'],
            }
    return {
        'message_id': None,
        'year': True,
        'month': True,
        'days': True,
        'hours': True,
        'minutes': True,
        'seconds': True,
        'day_of_week': True,
        'day_progress': True,
        'year_progress': True,
        'update_interval': 5,
        'timezone_offset': 5,
        'field_order': ['year','month','days','day_of_week','hours','minutes','seconds','day_progress','year_progress'],
    }

def write_config(message_id, settings=None):
    config = configparser.ConfigParser()
    config.optionxform = str
    
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        config.read(CONFIG_FILE)
        
        if not config.has_section('Telegram'):
            config.add_section('Telegram')
        
        config.set('Telegram', 'message_id', str(message_id))
        
        lines = content.split('\n')
        new_lines = []
        in_telegram_section = False
        message_id_updated = False
        
        for line in lines:
            if line.strip() == '[Telegram]':
                in_telegram_section = True
                new_lines.append(line)
            elif line.strip().startswith('[') and line.strip() != '[Telegram]':
                in_telegram_section = False
                new_lines.append(line)
            elif in_telegram_section and line.strip().startswith('message_id'):
                new_lines.append(f'message_id = {message_id}')
                message_id_updated = True
            else:
                new_lines.append(line)
        
        if not message_id_updated:
            for i, line in enumerate(new_lines):
                if line.strip() == '[Telegram]':
                    new_lines.insert(i + 1, f'message_id = {message_id}')
                    break
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
    else:
        config.add_section('Telegram')
        config.set('Telegram', 'message_id', str(message_id))
        
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)

async def update_time_message():
    settings = load_settings()
    message_id = settings['message_id']
    tz = timezone(timedelta(hours=settings['timezone_offset']))
    
    while True:
        now = datetime.now(tz)

        field_generators = {
            'days': lambda: now.strftime('%d'),
            'month': lambda: now.strftime('%m'),
            'year': lambda: str(now.year),
            'day_of_week': lambda: f"'{now.strftime('%A')}'",
            'hours': lambda: now.strftime('%H'),
            'minutes': lambda: now.strftime('%M'),
            'seconds': lambda: now.strftime('%S'),
            'day_progress': lambda: f"{((now.hour * 3600 + now.minute * 60 + now.second) / 86400) * 100:.2f}%",
            'year_progress': lambda: f"{((now - datetime(year=now.year, month=1, day=1, tzinfo=tz)).total_seconds() / (datetime(year=now.year, month=12, day=31, hour=23, minute=59, second=59, tzinfo=tz) - datetime(year=now.year, month=1, day=1, tzinfo=tz)).total_seconds()) * 100:.6f}%"
        }
        
        field_names = {
            'days': 'day',
            'month': 'month',
            'year': 'year',
            'day_of_week': 'dayOfWeek',
            'hours': 'hour',
            'minutes': 'minute',
            'seconds': 'seconds',
            'day_progress': 'dayProgress',
            'year_progress': 'yearProgress'
        }
        
        fields = []
        
        for field in settings['field_order']:
            if field in settings and settings[field] and field in field_generators:
                value = field_generators[field]()
                field_name = field_names[field]
                fields.append(f"  {field_name}: {value}")
        
        fields_text = ",\n".join(fields)
        if fields_text:
            fields_text += ",\n"
        
        text = (
            f"```javascript\n"
            f"const life = {{\n"
            f"{fields_text}"
            f"}}\n"
            f"```"
        )

        try:
            if message_id is None:
                msg = await bot.send_message(CHANNEL_ID, text)
                message_id = msg.message_id
                write_config(message_id, settings)
            else:
                await bot.edit_message_text(text, chat_id=CHANNEL_ID, message_id=message_id)
        except Exception as e:
            print(f'Error: {e}')
            if "message to edit not found" in str(e).lower():
                message_id = None
                if Path(CONFIG_FILE).exists():
                    Path(CONFIG_FILE).unlink() 

        await asyncio.sleep(settings['update_interval'])

async def main():
    asyncio.create_task(update_time_message())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
