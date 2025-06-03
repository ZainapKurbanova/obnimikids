from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from cart.models import CartItem
from .form import CheckoutForm
from .models import Order, OrderItem
from telegram import Bot
from django.conf import settings
import asyncio

async def send_telegram_message(chat_id, message):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product', 'size')
    total_price = sum(item.get_total_price() for item in cart_items)
    form = CheckoutForm(user=request.user)
    context = {'cart_items': cart_items, 'total_price': total_price, 'form': form}
    return render(request, 'orders/checkout.html', context)

@login_required
def process_order(request):
    if request.method == 'POST':
        form = CheckoutForm(request.user, request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            city = form.cleaned_data['city']
            address_detail = form.cleaned_data['address_detail']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            delivery_method = form.cleaned_data['delivery_method']
            telegram_id = form.cleaned_data.get('telegram_id')  # Поле для Telegram ID, если добавлено в форму

            form.save_to_profile(request.user)

            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items:
                messages.error(request, "Ваша корзина пуста.")
                return redirect('cart')

            total_price = sum(item.get_total_price() for item in cart_items)
            delivery_cost = 300 if delivery_method == 'post' else 500

            order = Order.objects.create(
                user=request.user,
                name=name,
                city=city,
                address_detail=address_detail,
                email=email,
                phone=phone,
                telegram_id=telegram_id,
                total_price=total_price,
                delivery_method=delivery_method,
                delivery_cost=delivery_cost,
                status='pending'
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    quantity=item.quantity,
                    price=item.product.price
                )

            cart_items.delete()

            # Сообщение клиенту
            client_message = (
                f"Здравствуйте, {name}!\n\n"
                f"Ваш заказ №{order.id} на сумму {order.get_total_with_delivery()} ₽ успешно оформлен.\n"
                f"Для оплаты с вами свяжется администратор в Telegram.\n"
                f"Статус заказа вы можете отслеживать в личном кабинете.\n\n"
                f"С уважением,\nOBNIMI Kids"
            )

            # Сообщение администратору
            admin_message = (
                f"Новый заказ №{order.id}!\n"
                f"Клиент: {name}\n"
                f"Телефон: {phone}\n"
                f"Email: {email}\n"
                f"Сумма: {order.get_total_with_delivery()} ₽\n"
                f"Статус: Ожидает оплаты"
            )

            # Асинхронная отправка сообщений
            if telegram_id:
                asyncio.run(send_telegram_message(telegram_id, client_message))
            asyncio.run(send_telegram_message(settings.ADMIN_TELEGRAM_ID, admin_message))

            messages.success(
                request,
                "Заказ успешно оформлен! Но требует оплаты! Для оплаты с вами свяжется администратор в Telegram. "
                "Статус можете отслеживать в личном кабинете."
            )
            return redirect('checkout')
        else:
            cart_items = CartItem.objects.filter(user=request.user)
            total_price = sum(item.get_total_price() for item in cart_items)
            context = {'cart_items': cart_items, 'total_price': total_price, 'form': form}
            return render(request, 'orders/checkout.html', context)
    return HttpResponse("Метод не поддерживается", status=405)