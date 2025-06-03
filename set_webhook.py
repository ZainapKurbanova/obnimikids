import asyncio
from telegram import Bot
from django.conf import settings
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obnimikids.settings')
django.setup()

async def set_webhook():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    webhook_url = f"https://obnimikids.ru/webhook/"
    await bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}")

if __name__ == '__main__':
    asyncio.run(set_webhook())