import os
import django
from telegram.ext import Application, CommandHandler, Dispatcher
from telegram import Update, Bot
from django.conf import settings
import logging
from asgiref.sync import sync_to_async

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obnimikids.settings')
django.setup()

# Импорты моделей
from orders.models import Order

async def get_id(update: Update, context):
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Ваш Telegram ID: {user_id}")

async def orders(update: Update, context):
    if str(update.message.from_user.id) != settings.ADMIN_TELEGRAM_ID:
        await update.message.reply_text("Доступ запрещён. Эта команда только для администратора.")
        logger.warning(f"Несанкционированный доступ к /orders: chat_id={update.message.from_user.id}")
        return

    pending_orders = await sync_to_async(list)(Order.objects.filter(status='pending'))
    if not pending_orders:
        await update.message.reply_text("Нет заказов в статусе 'Ожидает оплаты'.")
        return

    message = "Список заказов в статусе 'Ожидает оплаты':\n\n"
    for order in pending_orders:
        message += (
            f"Заказ №{order.id}\n"
            f"Клиент: {order.name}\n"
            f"Сумма: {order.get_total_with_delivery()} ₽\n"
            f"Telegram ID: {order.telegram_id}\n"
            f"Email: {order.email}\n"
            f"Статус: {order.get_status_display()}\n"
            f"---\n"
        )
    await update.message.reply_text(message, parse_mode='HTML')
    logger.info(f"Администратор запросил список заказов: chat_id={update.message.from_user.id}")

async def set_status(update: Update, context):
    if str(update.message.from_user.id) != settings.ADMIN_TELEGRAM_ID:
        await update.message.reply_text("Доступ запрещён. Эта команда только для администратора.")
        logger.warning(f"Несанкционированный доступ к /setstatus: chat_id={update.message.from_user.id}")
        return

    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Использование: /setstatus <order_id> <status>\nСтатусы: paid, shipped, delivered, cancelled")
            return

        order_id, status = args
        order = await sync_to_async(Order.objects.get)(id=order_id)

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if status not in valid_statuses:
            await update.message.reply_text(f"Недопустимый статус. Доступные статусы: {', '.join(valid_statuses)}")
            return

        order.status = status
        await sync_to_async(order.save)()
        await update.message.reply_text(f"Статус заказа №{order_id} изменён на: {order.get_status_display()}")
        logger.info(f"Статус заказа №{order_id} изменён на {status} администратором: chat_id={update.message.from_user.id}")
    except Order.DoesNotExist:
        await update.message.reply_text(f"Заказ №{order_id} не найден.")
        logger.error(f"Заказ №{order_id} не найден для изменения статуса")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")
        logger.error(f"Ошибка при изменении статуса заказа: {str(e)}")

async def error_handler(update: Update, context):
    logger.error(f"Ошибка в боте: {context.error}", exc_info=context.error)
    if update and update.message:
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
    if settings.ADMIN_TELEGRAM_ID:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=settings.ADMIN_TELEGRAM_ID,
            text=f"Ошибка в боте: {context.error}"
        )

# Инициализация диспетчера для вебхуков
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
application.add_handler(CommandHandler("getid", get_id))
application.add_handler(CommandHandler("orders", orders))
application.add_handler(CommandHandler("setstatus", set_status))
application.add_error_handler(error_handler)

# Создание диспетчера
dispatcher = application.dispatcher