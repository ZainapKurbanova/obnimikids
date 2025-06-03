from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from telegram import Bot
from django.conf import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

async def send_status_update(chat_id, order):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    message = (
        f"Здравствуйте, {order.name}!\n\n"
        f"Статус вашего заказа №{order.id} обновлён: {order.get_status_display()}.\n"
        f"{'Ожидается доставка в ближайшие дни.' if order.status == 'paid' else ''}\n"
        f"С уважением,\nOBNIMI Kids"
    )
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
        logger.info(f"Уведомление о статусе отправлено: chat_id={chat_id}, order_id={order.id}")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о статусе для chat_id={chat_id}: {e}")

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    if instance.status in ['paid', 'shipped', 'delivered'] and instance.telegram_id:
        asyncio.run(send_status_update(instance.telegram_id, instance))
    else:
        logger.warning(f"Не отправлено уведомление для заказа №{instance.id}: telegram_id={instance.telegram_id}")