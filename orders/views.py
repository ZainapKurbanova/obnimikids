from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from cart.models import CartItem
from .form import CheckoutForm
from .models import Order, OrderItem

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

            subject = f'Заказ #{order.id} успешно оформлен'
            message = f'Здравствуйте, {name}!\n\nВаш заказ на сумму {order.get_total_with_delivery()} ₽ успешно оформлен.\nМы свяжемся с вами для подтверждения.\n\nС уважением,\nOBNIMI Kids'
            send_mail(subject, message, 'your-email@gmail.com', [email], fail_silently=False)

            messages.success(request, f"Заказ на сумму {order.get_total_with_delivery()} ₽ успешно оформлен! Переходите к оплате.")
            return redirect('checkout')
        else:
            cart_items = CartItem.objects.filter(user=request.user)
            total_price = sum(item.get_total_price() for item in cart_items)
            context = {'cart_items': cart_items, 'total_price': total_price, 'form': form}
            return render(request, 'orders/checkout.html', context)
    return HttpResponse("Метод не поддерживается", status=405)