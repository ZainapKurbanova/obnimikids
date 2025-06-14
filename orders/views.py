from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from cart.models import CartItem
from .form import CheckoutForm
from .models import Order, OrderItem
from django.db.models import Count
from telegram import Bot
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def is_admin(user):
    return user.is_authenticated and user.is_superuser

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

            # Telegram уведомление админу
            try:
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                for chat_id in settings.TELEGRAM_ADMIN_CHAT_IDS:
                    bot.send_message(
                        chat_id=chat_id,
                        text=f"📦 Новый заказ #{order.id}\n👤 Пользователь: @{request.user.username}\n📧 Email: {request.user.email}"
                    )
            except Exception as e:
                logger.error(f"Ошибка при отправке Telegram-сообщения: {e}")

            messages.success(
                request,
                "Ваш заказ оформлен! С вами в течение 30 минут свяжется администратор для оплаты! "
                "За заказом можете отследить в личном кабинете."
            )
            return redirect('profile')
        else:
            cart_items = CartItem.objects.filter(user=request.user)
            total_price = sum(item.get_total_price() for item in cart_items)
            context = {'cart_items': cart_items, 'total_price': total_price, 'form': form}
            return render(request, 'orders/checkout.html', context)
    return HttpResponse("Метод не поддерживается", status=405)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    users_with_orders = Order.objects.values('user__username', 'user__email').annotate(
        order_count=Count('id')).order_by('-order_count')
    total_orders = Order.objects.count()
    total_revenue = sum(order.get_total_with_delivery() for order in Order.objects.all())
    status_counts = Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    status_display_map = dict(Order.STATUS_CHOICES)
    status_labels = [status_display_map[item['status']] for item in status_counts]
    status_data = [item['count'] for item in status_counts]
    top_products = OrderItem.objects.values('product__name').annotate(total=Count('product')).order_by('-total')[:5]
    top_products_labels = [item['product__name'] for item in top_products]
    top_products_data = [item['total'] for item in top_products]
    context = {
        'users_with_orders': users_with_orders,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'status_labels': status_labels,
        'status_data': status_data,
        'top_products_labels': top_products_labels,
        'top_products_data': top_products_data,
    }
    return render(request, 'orders/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_orders(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    orders = Order.objects.filter(user=user).select_related('user').prefetch_related('items')
    orders = orders.order_by('status', '-created_at')

    if request.method == "POST":
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        try:
            order = Order.objects.get(id=order_id)
            old_status = order.status
            order.status = new_status
            order.save()
            logger.info(f"Статус заказа #{order_id} изменён на {new_status}")
            messages.success(request, f"Статус заказа #{order_id} успешно обновлён.")

            # Telegram уведомление пользователю
            try:
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                bot.send_message(
                    chat_id=order.user.telegram_chat_id,
                    text=f"🔄 Статус вашего заказа #{order.id} изменён на: {order.get_status_display()}"
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке Telegram-уведомления: {e}")

        except Order.DoesNotExist:
            messages.error(request, "Заказ не найден.")

    context = {
        'user': user,
        'orders': orders,
    }
    return render(request, 'orders/admin_user_orders.html', context)
